import json

from helper import util_methods

from dataclasses import dataclass, field

SECTION_PREFIX = "Section: "
DEFAULT_SECTION_NAME = "-"

@dataclass()
class ExporterConfiguration:
    todoist_token: str
    export_directory: str
    download_attachments: bool


@dataclass()
class DueDateInternal:
    date: str
    is_recurring: bool
    due_string: str

    def to_dict(self):
        return {
            "date": self.date,
            "is_recurring": self.is_recurring,
            "due_string": self.due_string
        }


@dataclass()
class DurationInternal:
    amount: int
    unit: str

    def to_dict(self):
        return {
            "amount": self.amount,
            "unit": self.unit
        }


@dataclass()
class AttachmentInternal:
    file_type: str
    file_url: str
    resource_type: str
    local_file_name: str

    def to_dict(self):
        return {
            "file_type": self.file_type,
            "file_url": self.file_url,
            "resource_type": self.resource_type,
            "local_file_name": self.local_file_name
        }


@dataclass()
class CommentInternal:
    content: str
    date: str
    attachment: AttachmentInternal

    def to_dict(self):
        return {
            "content": util_methods.format_newline_text_to_multiline_list(self.content),
            "date": self.date,
            "attachment": self.attachment.to_dict() if self.attachment else None,
        }


@dataclass()
class TaskInternal:
    task_created_at: str
    task_content: str
    task_description: str
    task_priority: int
    task_due_date: DueDateInternal
    task_duration: DurationInternal
    project_id: str
    parent_id: str
    section_id: str
    labels: list[str]

    comments: list[CommentInternal] = field(init=False)
    child_tasks: list = field(init=False)

    def __post_init__(self):
        self.comments = []
        self.child_tasks = []

    def add_child_task(self, task):
        self.child_tasks.append(task)

    def add_comment(self, comment: CommentInternal):
        self.comments.append(comment)

    def to_dict(self):
        return {
            "task_content": self.task_content,
            "task_description": util_methods.format_newline_text_to_multiline_list(self.task_description),
            "labels": self.labels,
            "task_created_at": self.task_created_at,
            "task_priority": self.task_priority,
            "task_due_date": self.task_due_date.to_dict() if self.task_due_date else None,
            "task_duration": self.task_duration.to_dict() if self.task_duration else None,
            "comments": [comment.to_dict() for comment in self.comments],
            "child_tasks": [child_task.to_dict() for child_task in self.child_tasks]
        }


@dataclass()
class SectionInternal:
    project_id: str
    order: int
    name: str


@dataclass()
class ProjectInternal:
    project_name: str
    parent_id: str

    tasks: dict = field(init=False)
    child_projects: list = field(init=False)

    def __post_init__(self):
        default_section = SECTION_PREFIX + DEFAULT_SECTION_NAME
        self.tasks = {default_section: []}
        self.child_projects = []

    def add_task(self, section_name: str, task: TaskInternal):
        section_name_long = SECTION_PREFIX + section_name
        if section_name_long not in self.tasks:
            self.tasks[section_name_long] = []

        self.tasks[section_name_long].append(task)

    def add_child_project(self, child_project):
        self.child_projects.append(child_project)

    def collect_tasks_within_sections(self):
        tasks_list = {}
        for section_name, tasks in self.tasks.items():
            tasks_list[section_name] = [task.to_dict() for task in tasks]

        return tasks_list

    def to_dict(self):
        return {
            "project_name": self.project_name,
            "tasks": self.collect_tasks_within_sections(),
            "child_projects": [child_project.to_dict() for child_project in self.child_projects],
        }


@dataclass()
class TodoIstInternal:
    projects_list: list = field(init=False)

    def __post_init__(self):
        self.projects_list = []

    def add_project(self, project: ProjectInternal):
        self.projects_list.append(project)

    def to_json(self):
        projects_list = [project.to_dict() for project in self.projects_list]
        filtered_projects_list = util_methods.remove_empty_fields(projects_list)
        return json.dumps(filtered_projects_list, indent=4, ensure_ascii=False)