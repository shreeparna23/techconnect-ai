
import sqlite3
import json
from pathlib import Path

# Store the database beside this Python file
DB_PATH = Path(__file__).resolve().parent / "techconnect.db"


def get_connection():
    connection = sqlite3.connect(str(DB_PATH))
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database():
    with get_connection() as connection:
        connection.executescript("""
            CREATE TABLE IF NOT EXISTS profiles (
                name TEXT PRIMARY KEY,
                profile_data TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS teams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                project TEXT NOT NULL,
                description TEXT NOT NULL,
                skills TEXT NOT NULL,
                max_members INTEGER NOT NULL,
                creator TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS team_members (
                team_id INTEGER NOT NULL,
                student_name TEXT NOT NULL,
                PRIMARY KEY (team_id, student_name),
                FOREIGN KEY (team_id)
                    REFERENCES teams(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS join_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                team_id INTEGER NOT NULL,
                student_name TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                UNIQUE (team_id, student_name),
                FOREIGN KEY (team_id)
                    REFERENCES teams(id) ON DELETE CASCADE
            );
        """)


def save_profile(profile):
    name = profile.get("name", "").strip()

    if not name:
        raise ValueError("Profile must have a student name.")

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO profiles (name, profile_data)
            VALUES (?, ?)
            ON CONFLICT(name) DO UPDATE SET
                profile_data = excluded.profile_data
            """,
            (name, json.dumps(profile))
        )


def load_profiles():
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT profile_data FROM profiles ORDER BY name"
        ).fetchall()

    return [json.loads(row["profile_data"]) for row in rows]


def create_team(team):
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO teams
            (name, project, description, skills, max_members, creator)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                team["name"],
                team["project"],
                team["description"],
                json.dumps(team.get("skills", [])),
                team["max_members"],
                team["creator"]
            )
        )

        team_id = cursor.lastrowid

        connection.execute(
            """
            INSERT INTO team_members (team_id, student_name)
            VALUES (?, ?)
            """,
            (team_id, team["creator"])
        )

    return team_id


def load_teams():
    with get_connection() as connection:
        teams = connection.execute(
            "SELECT * FROM teams ORDER BY id DESC"
        ).fetchall()

        result = []

        for team in teams:
            team_id = team["id"]

            members = connection.execute(
                """
                SELECT student_name FROM team_members
                WHERE team_id = ? ORDER BY student_name
                """,
                (team_id,)
            ).fetchall()

            requests = connection.execute(
                """
                SELECT student_name FROM join_requests
                WHERE team_id = ? AND status = 'pending'
                ORDER BY id
                """,
                (team_id,)
            ).fetchall()

            result.append({
                "id": team_id,
                "name": team["name"],
                "project": team["project"],
                "description": team["description"],
                "skills": json.loads(team["skills"]),
                "max_members": team["max_members"],
                "creator": team["creator"],
                "members": [row["student_name"] for row in members],
                "requests": [row["student_name"] for row in requests]
            })

    return result


def request_to_join(team_id, student_name):
    with get_connection() as connection:
        team = connection.execute(
            "SELECT max_members FROM teams WHERE id = ?",
            (team_id,)
        ).fetchone()

        if team is None:
            return False, "Team not found."

        member_count = connection.execute(
            "SELECT COUNT(*) FROM team_members WHERE team_id = ?",
            (team_id,)
        ).fetchone()[0]

        if member_count >= team["max_members"]:
            return False, "This team is full."

        is_member = connection.execute(
            """
            SELECT 1 FROM team_members
            WHERE team_id = ? AND student_name = ?
            """,
            (team_id, student_name)
        ).fetchone()

        if is_member:
            return False, "You are already a team member."

        existing = connection.execute(
            """
            SELECT status FROM join_requests
            WHERE team_id = ? AND student_name = ?
            """,
            (team_id, student_name)
        ).fetchone()

        if existing:
            if existing["status"] == "pending":
                return False, "Your request is already pending."

            if existing["status"] == "accepted":
                return False, "You have already joined this team."

            connection.execute(
                """
                UPDATE join_requests SET status = 'pending'
                WHERE team_id = ? AND student_name = ?
                """,
                (team_id, student_name)
            )
        else:
            connection.execute(
                """
                INSERT INTO join_requests
                (team_id, student_name, status)
                VALUES (?, ?, 'pending')
                """,
                (team_id, student_name)
            )

    return True, "Join request sent!"


def respond_to_request(team_id, student_name, accept):
    with get_connection() as connection:
        team = connection.execute(
            "SELECT max_members FROM teams WHERE id = ?",
            (team_id,)
        ).fetchone()

        if team is None:
            return False, "Team not found."

        request = connection.execute(
            """
            SELECT status FROM join_requests
            WHERE team_id = ? AND student_name = ?
            """,
            (team_id, student_name)
        ).fetchone()

        if request is None or request["status"] != "pending":
            return False, "No pending request found."

        if accept:
            member_count = connection.execute(
                "SELECT COUNT(*) FROM team_members WHERE team_id = ?",
                (team_id,)
            ).fetchone()[0]

            if member_count >= team["max_members"]:
                return False, "This team is full."

            connection.execute(
                """
                INSERT OR IGNORE INTO team_members
                (team_id, student_name) VALUES (?, ?)
                """,
                (team_id, student_name)
            )

            status = "accepted"
        else:
            status = "declined"

        connection.execute(
            """
            UPDATE join_requests SET status = ?
            WHERE team_id = ? AND student_name = ?
            """,
            (status, team_id, student_name)
        )

    return True, "Request accepted!" if accept else "Request declined!"


# Create the tables when this module is imported
initialize_database()
