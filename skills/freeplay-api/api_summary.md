## API Operations

### Observability

**Update Session Metadata** (`patch_update_session_metadata`)  
Merge custom metadata into an existing session. Use to enrich sessions with post-hoc context like user ID or business metrics.

**Record Completion** (`post_record_completion`)  
Log an LLM completion with its prompt, response, and metadata. This is the primary endpoint for observability. Sessions are created implicitly—just generate a session_id client-side (UUID v4).

**Record Trace** (`post_record_trace`)  
Log a trace event representing a single execution step (e.g., tool call, retrieval, or sub-agent). Use to add structure to multi-step agentic workflows.

**Update Trace By ID** (`patch_update_trace_by_id`)  
Modify an existing trace's metadata or outcome. Use to enrich traces with post-hoc context.

**Update Trace Metadata** (`patch_update_trace_metadata`)  
Merge custom metadata into an existing trace. Use to enrich traces with post-hoc context like business metrics or execution details.

**Update Trace By OpenTelemetry Span ID** (`patch_update_trace_by_otel_span_id`)  
Update a trace using its OpenTelemetry span ID. Use when integrating with OpenTelemetry instrumentation.

### Feedback

**Create Completion Feedback** (`post_create_completion_feedback`)  
Submit a feedback event (e.g., thumbs up/down, rating, or human correction) for a completion. Use to capture human annotations for model evaluation.

**Create Trace Feedback** (`post_trace_feedback`)  
Submit feedback for a specific trace. Use to annotate individual steps in multi-step workflows.

### Search & Analytics

**Search Completions** (`post_search_completions`)  
Query LLM completions using advanced filters. Use to find specific prompts and responses, filter by evaluation results or metadata, prompt templates, latency, and more.

**Search Sessions** (`post_search_sessions`)  
Query sessions using advanced filters. Use to find specific conversations or filter by metadata.

**Search Traces** (`post_search_traces`)  
Query traces using advanced filters. Use to find specific trace executions, filter by metadata, or analyze trace patterns.

**Get All Completion Statistics** (`post_get_all_completion_summaries`)  
Retrieve aggregate evaluation statistics across all prompts for a date range. Use for dashboard metrics or trend analysis. Maximum date range is 30 days.

**Get Completion Statistics** (`post_get_completion_summary`)  
Retrieve evaluation statistics for a specific prompt template. Use to track quality metrics for individual prompts. Maximum date range is 30 days.

**List Sessions** (`get_get_sessions_filtered`)  
Retrieve sessions with their completions, ordered by most recent first. Use to display conversation history or analyze LLM usage patterns. Filter by custom metadata using query parameters prefixed with `custom_metadata.`.

### Prompt Templates

**Create Prompt Template Version By ID** (`post_create_template_version_by_id`)  
Create a new version of a prompt template, referenced by its unique ID. A new version is created only if there is no existing version with identical content, model, LLM parameters, version name/description, and schemas.

**List Prompt Template Versions** (`get_list_prompt_template_versions`)  
Retrieve all versions of a prompt template. Use to view version history or compare changes over time.

**Get Prompt Template Version By ID** (`get_get_by_template_version_id`)  
Retrieve a specific prompt template version by ID.

**Get Bound Prompt Template Version By ID** (`post_get_bound_by_template_version_id`)  
Retrieve a prompt template version with variables bound to provided values.

**Delete Prompt Template Version** (`delete_delete_template_version`)  
Delete a specific prompt template version.

**Update Environment For Prompt Template Version** (`post_update_template_version_environments`)  
Deploy a prompt version to one or more environments. Use to promote versions through dev, staging, and production.

**Create Prompt Template Version By Name** (`post_create_template_version_by_name`)  
Create a new version of a prompt template, referenced by a string or name you define. Set `create_template_if_not_exists=true` to auto-create the template if it doesn't exist.

**List Prompt Templates** (`get_list_prompt_templates`)  
Retrieve all prompt templates in a project. Use to discover available templates or build template management UIs.

**Create Prompt Template** (`post_create_prompt_template`)  
Create a new prompt template without any versions. Use when you need to reserve a template name before adding versions.

**Get All Prompt Templates By Environment** (`get_get_all_by_environment`)  
Retrieve all prompt templates deployed to a specific environment.

**Get Prompt Template** (`get_get_prompt_template`)  
Retrieve a prompt template's metadata by ID. Use to check if a template exists or get its latest version ID.

**Update Prompt Template** (`patch_update_prompt_template`)  
Rename a prompt template. Use when refactoring template names across your codebase.

**Delete Prompt Template** (`delete_delete_prompt_template`)  
Archive a prompt template and all its versions. Use when retiring templates that are no longer needed. This is a soft delete.

**Get Prompt Template By Name And Environment** (`get_get_by_name_and_environment`)  
Retrieve a prompt template by name and environment.

**Get Bound Prompt Template By Name And Environment** (`post_get_bound_by_name_and_environment`)  
Retrieve a prompt template by name and environment with variables bound to provided values.

### Test Runs

**Create Test Run** (`post_create_with_test_cases`)  
Create a new test run to evaluate a prompt or agent against a dataset.

**List Test Runs** (`get_get_test_runs`)  
Retrieve all test runs in a project.

**Get Test Run Results** (`get_get_test_run_results`)  
Retrieve detailed results for a specific test run.

### Evaluation Criteria

**Create Evaluation Criteria** (`post_create_evaluation_criteria`)  
Create a new evaluation criteria for assessing LLM outputs.

**List Evaluation Criteria** (`get_list_evaluation_criteria`)  
Retrieve all evaluation criteria in a project. Use to discover available criteria or build criteria management UIs.

**Get Evaluation Criteria** (`get_get_evaluation_criteria`)  
Retrieve an evaluation criteria's configuration by ID. Use to inspect criteria settings or get the latest version ID.

**Delete Evaluation Criteria** (`delete_delete_evaluation_criteria`)  
Permanently delete an evaluation criteria and all its versions. Use when retiring criteria no longer needed.

**Disable Criteria** (`patch_disable_criteria`)  
Deactivate an evaluation criteria without deleting it. Use to temporarily pause the use of a given criteria in evaluations.

**Enable Criteria** (`patch_enable_criteria`)  
Activate an evaluation criteria for use in test runs and online evaluations.

**Reorder Criteria** (`patch_reorder_criteria`)  
Change the display order of evaluation criteria in the Freeplay UI. Use to organize criteria in a logical sequence for human review workflows.

**Create Evaluation Criteria Version** (`post_create_criteria_version`)  
Create a new version of an evaluation criteria.

**List Evaluation Criteria Versions** (`get_list_criteria_versions`)  
Retrieve all versions of an evaluation criteria. Use to view version history or compare changes.

**Get Evaluation Criteria Version** (`get_get_criteria_version`)  
Retrieve a specific evaluation criteria version by ID.

**Delete Evaluation Criteria Version** (`delete_delete_criteria_version`)  
Delete a specific evaluation criteria version.

**Deploy Evaluation Criteria Version** (`post_deploy_criteria_version`)  
Deploy an evaluation criteria version to specific environments.

### Prompt Datasets

**Get Test Cases By ID** (`get_get_test_cases_by_id`)  
Retrieve test cases for a prompt dataset by dataset ID.

**Upload Test Cases** (`post_upload_test_cases`)  
Upload test cases to a prompt dataset in bulk.

**Get Test Cases By Name** (`get_get_test_cases_by_name`)  
Retrieve test cases for a prompt dataset by dataset name.

**List Prompt Test Cases** (`get_get_prompt_dataset_test_cases`)  
Retrieve all test cases (row-level values) in a prompt dataset. Use to review dataset contents or export for analysis.

**Bulk Create Prompt Test Cases** (`post_bulk_create_prompt_dataset_test_cases`)  
Add multiple test cases to a prompt dataset in a single request. Use for batch imports from production completions. Maximum 100 test cases per request.

**Bulk Delete Prompt Test Cases** (`delete_bulk_delete_prompt_dataset_test_cases`)  
Remove multiple prompt test cases in a single request. Use for batch cleanup operations. Maximum 100 test cases per request.

**Get Prompt Test Case** (`get_get_prompt_dataset_test_case`)  
Retrieve a specific prompt test case by ID. Use to inspect test case details or debug test run results.

**Update Prompt Test Case** (`patch_update_prompt_dataset_test_case`)  
Modify an existing prompt test case's inputs, outputs, or metadata. Use to correct errors or update expected outputs.

**Delete Prompt Test Case** (`delete_delete_prompt_dataset_test_case`)  
Remove a test case from a prompt dataset. Use to clean up invalid or outdated test cases.

**Get Prompt Dataset By ID** (`get_get_by_id`)  
Retrieve a prompt dataset's metadata by ID.

**Get Prompt Dataset By Name** (`get_get_by_name`)  
Retrieve a prompt dataset's metadata by name.

**Create Prompt Dataset** (`post_create_prompt_dataset`)  
Create a new dataset for prompt-level testing. Use to organize test cases for evaluating prompt templates.

**List Prompt Datasets** (`get_get_prompt_datasets`)  
Retrieve all prompt-level datasets in a project. Use to discover available datasets for prompt test runs.

**Get Prompt Dataset** (`get_get_prompt_dataset`)  
Retrieve a prompt dataset's metadata by ID. Use to check dataset configuration or compatible prompts.

**Update Prompt Dataset** (`patch_update_prompt_dataset`)  
Modify a prompt dataset's name, description, or compatible prompts. Use to evolve datasets as prompt requirements change.

**Delete Prompt Dataset** (`delete_delete_prompt_dataset`)  
Archive a prompt dataset and its test cases. Use when retiring datasets no longer needed.

### Agent Datasets

**List Agent Test Cases** (`get_get_agent_dataset_test_cases`)  
Retrieve all test cases (row-level values) in an agent dataset. Use to review dataset contents or export for analysis.

**Bulk Create Agent Test Cases** (`post_bulk_create_agent_dataset_test_cases`)  
Add multiple test cases to an agent dataset in a single request. Use for batch imports from production traces. Maximum 100 test cases per request.

**Bulk Delete Agent Test Cases** (`delete_bulk_delete_agent_dataset_test_cases`)  
Remove multiple agent test cases in a single request. Use for batch cleanup operations. Maximum 100 test cases per request.

**Get Agent Test Case** (`get_get_agent_dataset_test_case`)  
Retrieve a specific agent test case by ID. Use to inspect test case details or debug test run results.

**Update Agent Test Case** (`patch_update_agent_dataset_test_case`)  
Modify an existing agent test case's inputs, outputs, or metadata. Use to correct errors or update expected outputs.

**Delete Agent Test Case** (`delete_delete_agent_dataset_test_case`)  
Remove a test case from an agent dataset. Use to clean up invalid or outdated test cases.

**Create Agent Dataset** (`post_create_agent_dataset`)  
Create a new dataset for agent-level testing. Use to organize test cases for evaluating full agent workflows.

**List Agent Datasets** (`get_get_agent_datasets`)  
Retrieve all agent-level datasets in a project. Use to discover available datasets for agent test runs.

**Get Agent Dataset** (`get_get_agent_dataset`)  
Retrieve an agent dataset's metadata by ID. Use to check dataset configuration or compatible agents.

**Update Agent Dataset** (`patch_update_agent_dataset`)  
Modify an agent dataset's name, description, or compatible agents. Use to evolve datasets as agent requirements change.

**Delete Agent Dataset** (`delete_delete_agent_dataset`)  
Archive an agent dataset and its test cases. Use when retiring datasets no longer needed.

### Configuration

**Create Project** (`post_create_project`)  
Create a new project in your workspace. Use to organize prompts, datasets, and observability data by team or application.

**List Projects** (`get_get_projects`)  
Retrieve all projects accessible to the current user. Use to discover available projects or build project selection UIs.

**Get Project** (`get_get_project`)  
Retrieve the current project's details. Use to check project settings like spend limits or data retention.

**Update Project** (`put_update_project`)  
Modify project settings like name, visibility, or resource limits. Requires project admin role.

**Delete Project** (`delete_delete_project`)  
Delete a project and all its associated data.

**Add Project Member** (`post_add_member`)  
Grant a user access to the project with a specified role. Requires project admin role.

**List Project Members** (`get_list_members`)  
Retrieve all users with access to the project and their roles. Use for access management or auditing.

**Remove Project Member** (`delete_remove_member`)  
Revoke a user's access to the project. Requires project admin role.

**Update Project Member** (`patch_update_member`)  
Change a user's role in the project. Requires project admin role.

**List Environments** (`get_list_environments`)  
Retrieve all deployment environments in your workspace. Use to discover available environments for prompt deployment.

**Create Environment** (`post_create_environment`)  
Create a new deployment environment. Use to add environments beyond Freeplay defaults, like staging or feature branches.

**Update Environment** (`patch_update_environment`)  
Rename an existing environment. Use when consolidating or reorganizing deployment targets.

**Delete Environment** (`delete_delete_environment`)  
Remove an environment. Use when retiring deployment targets no longer in use.

**Create User** (`post_create_user`)  
Create a new user in your workspace. Requires account admin role. Use for automated user provisioning or SCIM integrations.

**List Users** (`get_list_users`)  
Retrieve all users in your workspace. Requires account admin role. Use for user management or access auditing.

**Get User** (`get_get_user`)  
Retrieve a user's details by ID. Requires account admin role. Use to check user settings or role assignments.

**Update User** (`patch_update_user`)  
Modify a user's name, role, or profile settings. Requires account admin role.

**Delete User** (`delete_delete_user`)  
Remove a user from your workspace. Requires account admin role. Use for offboarding or access revocation.

### Saved Searches

**List Saved Searches** (`get_list_filters`)  
Retrieve a paginated list of saved searches for the project.

**Create Saved Search** (`post_replicate_filter`)  
Create or upsert a saved search for the project.

**Get Saved Search** (`get_get_filter`)  
Retrieve details for a specific saved search by ID.

**Update Saved Search** (`put_update_filter`)  
Update an existing saved search.

**Delete Saved Search** (`delete_delete_filter`)  
Delete a saved search from the project.

### Models (Legacy)

**List Models** (`get_list_models`)  
Retrieve a paginated list of models for the project.

**Create Model** (`post_replicate_model`)  
Create or upsert a model for the project.

**Get Model** (`get_get_model`)  
Retrieve details for a specific model by ID.

**Update Model** (`put_update_model`)  
Update an existing model.

**Delete Model** (`delete_delete_model`)  
Delete a model from the project.
