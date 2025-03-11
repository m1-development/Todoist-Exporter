import os
import traceback
from datetime import datetime
from time import sleep

from todoist_api_python.api import TodoistAPI

from helper import util_methods, logger
from model.internal_classes import TodoIstInternal, ProjectInternal, TaskInternal, DueDateInternal, DurationInternal, \
    CommentInternal, AttachmentInternal, SectionInternal, DEFAULT_SECTION_NAME

if __name__ == "__main__":
    try:
        exporter_configuration = util_methods.read_exporter_configuration()
        logger.log_info(f"token: {exporter_configuration.todoist_token}")
    except Exception as error:
        logger.log_error(f"{error.__class__.__name__}: {error}")
        exit(1)

    path_divider = "\\" if os.name == 'nt' else "/"
    export_directory = exporter_configuration.export_directory
    if not os.path.exists(export_directory):
        os.makedirs(export_directory)

    api = TodoistAPI(exporter_configuration.todoist_token) # open an API session to TodoIst service
    try:
        logger.log_info("Getting all projects")
        all_projects = util_methods.call_api_with_retries(api.get_projects)
        projects_internal_byid = {}
        for project in all_projects:
            project_internal = ProjectInternal(project.name,
                                               project.parent_id)
            projects_internal_byid[project.id] = project_internal

        logger.log_info("Getting all tasks")
        all_tasks = util_methods.call_api_with_retries(api.get_tasks)
        tasks_internal_byid = {}
        for task in all_tasks:
            task_due_date = None
            if task.due is not None:
                task_due_date = DueDateInternal(task.due.date,
                                                task.due.is_recurring,
                                                task.due.string)

            task_duration = None
            if task.duration is not None:
                task_duration = DurationInternal(task.duration.amount,
                                                 task.duration.unit)

            task_internal = TaskInternal(task.created_at,
                                         task.content,
                                         task.description,
                                         task.priority,
                                         task_due_date,
                                         task_duration,
                                         task.project_id,
                                         task.parent_id,
                                         task.section_id,
                                         task.labels)

            if task.comment_count > 0:
                logger.log_info(f"Getting comments for task {task.id}")
                task_comments = util_methods.call_api_with_retries(api.get_comments, task_id=task.id)

                for comment in task_comments:
                    attachment = None
                    if comment.attachment is not None:
                        local_file_name = None
                        if comment.attachment.file_url is not None and exporter_configuration.download_attachments:
                            local_file_name = util_methods.download_attachment(exporter_configuration.todoist_token,
                                                                             comment.id,
                                                                             comment.attachment.file_url,
                                                                             export_directory,
                                                                             path_divider)

                        attachment = AttachmentInternal(comment.attachment.file_type,
                                                        comment.attachment.file_url,
                                                        comment.attachment.resource_type,
                                                        local_file_name)

                    comment_internal = CommentInternal(comment.content,
                                                       comment.posted_at,
                                                       attachment)

                    task_internal.add_comment(comment_internal)
                    sleep(0.5)  # little rate limit for api requests

            tasks_internal_byid[task.id] = task_internal

        logger.log_info("Getting all sections")
        all_sections = util_methods.call_api_with_retries(api.get_sections)
        sections_internal_byid = {}
        for section in all_sections:
            section_internal = SectionInternal(section.project_id,
                                               section.order,
                                               section.name)

            sections_internal_byid[section.id] = section_internal

        logger.log_info("Build project and task dependencies")
        todoist = TodoIstInternal()

        for project_internal in projects_internal_byid.values():
            if project_internal.parent_id is None:
                todoist.add_project(project_internal)
            else:
                project_parent = projects_internal_byid[project_internal.parent_id]
                project_parent.add_child_project(project_internal)

        for task_internal in tasks_internal_byid.values():
            if task_internal.parent_id is None:
                related_project = projects_internal_byid[task_internal.project_id]

                section_name = DEFAULT_SECTION_NAME
                if task_internal.section_id is not None:
                    section_name = sections_internal_byid[task_internal.section_id].name

                related_project.add_task(section_name, task_internal)
            else:
                task_parent = tasks_internal_byid[task_internal.parent_id]
                task_parent.add_child_task(task_internal)

        date_time_prefix = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{date_time_prefix}_todoist_json_export.json"
        json = todoist.to_json()
        with open(export_directory + path_divider + filename, 'w', encoding='utf-8') as datei:
            datei.write(json)

    except Exception as error:
        error_details = traceback.format_exc()
        logger.log_error(error_details)