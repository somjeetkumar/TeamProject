import random
from datetime import timedelta

from faker import Faker

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model

from Task.models import (
    Organization,
    OrganizationMembership,
    Team,
    TeamMembership,
    Project,
    Task,
)


User = get_user_model()
fake = Faker()


class Command(BaseCommand):

    help = "Seed TaskFlow database with realistic test data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--tasks",
            type=int,
            default=10000,
            help="Number of tasks to create"
        )

    @transaction.atomic
    def handle(self, *args, **options):

        total_tasks = options["tasks"]

        self.stdout.write(
            self.style.WARNING(
                f"Starting database seeding for {total_tasks} tasks..."
            )
        )

        # -------------------------------------------------
        # Configuration
        # -------------------------------------------------

        ORGANIZATION_COUNT = 5
        USERS_PER_ORGANIZATION = 10
        TEAMS_PER_ORGANIZATION = 3
        PROJECTS_PER_TEAM = 4

        # -------------------------------------------------
        # 1. Create Organizations
        # -------------------------------------------------

        organizations = []

        for _ in range(ORGANIZATION_COUNT):

            organization = Organization(
                name=fake.unique.company()
            )

            organizations.append(organization)

        Organization.objects.bulk_create(organizations)

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {len(organizations)} organizations."
            )
        )

        # -------------------------------------------------
        # 2. Create Users
        # -------------------------------------------------

        users = []

        for _ in range(
            ORGANIZATION_COUNT * USERS_PER_ORGANIZATION
        ):

            username = fake.unique.user_name()

            user = User(
                username=username,
                email=fake.unique.email(),
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                is_active=True,
            )

            # Set a common password for seeded users
            user.set_password("Test@12345")

            users.append(user)

        User.objects.bulk_create(users)

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {len(users)} users."
            )
        )

        # -------------------------------------------------
        # 3. Create Organization Memberships
        # -------------------------------------------------

        organization_memberships = []

        organization_users = {}

        user_index = 0

        for organization in organizations:

            organization_users[organization.id] = []

            for position in range(USERS_PER_ORGANIZATION):

                user = users[user_index]

                organization_users[organization.id].append(user)

                # First user = owner
                # Next 2 users = admin
                # Remaining = member

                if position == 0:
                    role = "owner"

                elif position <= 2:
                    role = "admin"

                else:
                    role = "member"

                organization_memberships.append(
                    OrganizationMembership(
                        user=user,
                        organization=organization,
                        role=role,
                    )
                )

                user_index += 1

        OrganizationMembership.objects.bulk_create(
            organization_memberships
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {len(organization_memberships)} organization memberships."
            )
        )

        # -------------------------------------------------
        # 4. Create Teams
        # -------------------------------------------------

        teams = []

        for organization in organizations:

            for _ in range(TEAMS_PER_ORGANIZATION):

                team = Team(
                    name=fake.unique.bs().title(),
                    organization=organization,
                )

                teams.append(team)

        Team.objects.bulk_create(teams)

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {len(teams)} teams."
            )
        )

        # -------------------------------------------------
        # 5. Create Team Memberships
        # -------------------------------------------------

        team_memberships = []

        team_users = {}

        for team in teams:

            available_users = organization_users[
                team.organization_id
            ]

            # Select 5-8 users from same organization
            selected_users = random.sample(
                available_users,
                random.randint(5, 8)
            )

            team_users[team.id] = selected_users

            for user in selected_users:

                team_memberships.append(
                    TeamMembership(
                        user=user,
                        team=team,
                    )
                )

        TeamMembership.objects.bulk_create(
            team_memberships
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {len(team_memberships)} team memberships."
            )
        )

        # -------------------------------------------------
        # 6. Create Projects
        # -------------------------------------------------

        projects = []

        for team in teams:

            for _ in range(PROJECTS_PER_TEAM):

                project = Project(
                    name=fake.unique.catch_phrase(),
                    team=team,
                    description=fake.paragraph(
                        nb_sentences=3
                    ),
                )

                projects.append(project)

        Project.objects.bulk_create(projects)

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {len(projects)} projects."
            )
        )

        # -------------------------------------------------
        # 7. Create Tasks
        # -------------------------------------------------

        tasks = []

        statuses = [
            "todo",
            "in_progress",
            "done",
        ]

        priorities = [
            "low",
            "medium",
            "high",
        ]

        now = timezone.now()

        for _ in range(total_tasks):

            # Random project
            project = random.choice(projects)

            # Only users belonging to the project's team
            # can be assigned to the task.
            project_team_users = team_users[
                project.team_id
            ]

            assignee = random.choice(
                project_team_users
            )

            # created_by must belong to the
            # same organization as the project.
            project_organization_users = organization_users[
                project.team.organization_id
            ]

            created_by = random.choice(
                project_organization_users
            )

            created_at = now - timedelta(
                days=random.randint(0, 365),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59),
            )

            updated_at = created_at + timedelta(
                days=random.randint(0, 30),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59),
            )

            # Don't allow updated_at to be in the future
            if updated_at > now:
                updated_at = now

            task = Task(
                project=project,
                assignee=assignee,
                created_by=created_by,
                title=fake.sentence(
                    nb_words=random.randint(4, 10)
                ),
                description=fake.paragraph(
                    nb_sentences=random.randint(2, 5)
                ),
                status=random.choice(statuses),
                priority=random.choice(priorities),
                created_at=created_at,
                updated_at=updated_at,
            )

            tasks.append(task)

        # -------------------------------------------------
        # 8. Bulk create tasks
        # -------------------------------------------------

        Task.objects.bulk_create(
            tasks,
            batch_size=1000
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {len(tasks)} tasks."
            )
        )

        # -------------------------------------------------
        # Final summary
        # -------------------------------------------------

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                "======================================"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                "DATABASE SEEDING COMPLETED"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                "======================================"
            )
        )

        self.stdout.write(
            f"Organizations: {Organization.objects.count()}"
        )

        self.stdout.write(
            f"Users: {User.objects.count()}"
        )

        self.stdout.write(
            f"Organization Memberships: "
            f"{OrganizationMembership.objects.count()}"
        )

        self.stdout.write(
            f"Teams: {Team.objects.count()}"
        )

        self.stdout.write(
            f"Team Memberships: "
            f"{TeamMembership.objects.count()}"
        )

        self.stdout.write(
            f"Projects: {Project.objects.count()}"
        )

        self.stdout.write(
            f"Tasks: {Task.objects.count()}"
        )

        self.stdout.write("")

        self.stdout.write(
            self.style.WARNING(
                "Seed user password: Test@12345"
            )
        )