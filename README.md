# TodoIst-Exporter

This python application will export all projects and tasks from TodoIst into a single json file.

### Install instructions
- create an API token in the integration setting -> https://app.todoist.com/app/settings/integrations/developer
- copy 'sample_exporter_configuration.json' to 'exporter_configuration.json'
- edit 'exporter_configuration.json', add your API token and choose your export folder (windows/linux/mac paths are supported)
    - per default the folder 'export' in the project folder is taken, if the config for 'export_directory' is absent
    - per default attachments are downloaded, if the config for 'download_attachments' is absent

### Run instructions
- create a virtual environment in project folder
    - ```python -m venv myenv```
    - activate virtual environment 'myenv'
        - windows: ```myenv\Scripts\activate```
        - mac/linux: ```source myenv/bin/activate```
    - install requirements
        - ```pip install -r requirements.txt```

- run ```python todoist_exporter.py``` in project folder inside virtual environment 'myenv'

### Export results
- The exporter will create a json file with the following information
    - projects
    - tasks of each project with task sections ('-' is the default section)
    - the hierarchy of child projects and child task is included

Example output:
``` json
[
    {
        "project_name": "Project 1",
        "tasks": {
            "Section: -": [
                {
                    "task_content": "Task 1 of Project 1",
                    "task_description": [
                        "- Description bullet point 1",
                        "- [TodoIst-API Link](https://developer.todoist.com/rest/v2/#overview)"
                    ],
                    "task_created_at": "2025-03-09T12:00:00.000000Z",
                    "task_priority": 1
                },             
                {
                    "task_content": "Task 2 of Project 1",
                    "task_description": [
                        "- Description bullet point 1",
                        "- Description bullet point 2"
                    ],
                    "task_created_at": "2025-03-10T12:00:00.000000Z",
                    "task_priority": 2,
                    "child_tasks": [
                        {
                            "task_content": "Child Task 1 of Task 2",
                            "task_description": [
                                "- Description of child task"
                            ],
                            "task_created_at": "2025-03-10T12:05:00.000000Z",
                            "task_priority": 1
                        }       
                    ]
                }
            ],
            "Section: Section within project 1": [
                {
                    "task_content": "Task 3 in a section of project 1",
                    "task_description": [
                        "- Description bullet point 1"
                    ],
                    "task_created_at": "2025-03-11T12:00:00.000000Z",
                    "task_priority": 3
                }
            ]
        },
        "child_projects": [
            {
                "project_name": "Child project 1 below project 1",
                "tasks": {
                    "Section: -": [
                        {
                            "task_content": "Task 1 of child project 1",
                            "task_description": [
                                "- Description of task 1 in child project 1"
                            ],
                            "task_created_at": "2025-03-09T12:00:00.000000Z",
                            "task_priority": 4
                        }
                    ]
                }
            }
        ]
    }
]
```

### TodoIst-API
The official TodoIst-REST-API was used for this python script.</br>
It can be found under https://developer.todoist.com/rest/v2/#overview