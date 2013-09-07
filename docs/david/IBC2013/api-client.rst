
Orchestra API Client
********************

* api_root() -> client.about
* api_flush() -> client.flush()

* api_user_login() -> client.login(...)
* api_user_count() -> len(client.users)
* api_user_get() -> client.users.list()
* api_user_post() -> client.users.add(user)

* api_user_id_get(id) -> client.users[id]
* api_user_id_patch(id) -> client.users[id] = user
* api_user_id_delete(id) -> del client.users[id]

* api_media_count() -> len(client.medias)
* api_media_head() -> client.medias.list(head=True)
* api_media_get() -> client.medias.list() BUGGY (user is not assigned, should update Media class)
* api_media_post() -> client.medias.add(media)

* api_media_id_head(id) -> client.medias[id + '/HEAD']
* api_media_id_get(id) -> client.medias[id] BUGGY (user is not assigned, should update Media class)
* api_media_id_patch(id) -> client.medias[id] = media
* api_media_id_delete(id) -> del client.medias[id]

* api_environment_count() -> len(clients.environments)
* api_environment_get_head() -> clients.environments.list(head=True)
* api_environment_get() -> clients.environments.list()
* api_environment_post() -> clients.environments.add(environment) NOT YET IMPLEMENTED
* api_environment_name_get_head(name) -> clients.environments[name + '/HEAD']
* api_environment_name_get(name) -> clients.environments[name]
* api_environment_name_delete(name) -> del clients.environments[name]

* api_transform_profile_encoder() -> client.encoders
* api_transform_profile_count() -> len(client.transform_profiles)
* api_transform_profile_get() -> client.transform_profiles.list()
* api_transform_profile_post() -> client.transform_profiles.add(profile)

* api_transform_profile_id_get(id) -> client.transform_profiles[id]
* api_transform_profile_id_delete(id) -> del client.transform_profiles[id]

Set environment with client.transform_units.environment = 'amazon'

* api_transform_unit_count(environment) -> len(client.transform_units)
* api_transform_unit_get(environment) -> client.transform_units.list()
* api_transform_unit_post(environment) -> client.transform_units.add(num_units=2) - Ensure 2 units FIXME add != ensure
* api_transform_unit_delete(environment) -> FIXME ??
* api_transform_unit_number_get(environment, number) -> client.transform_units[number]
* api_transform_unit_number_delete(environment, number) -> del client.transform_units[number]

* api_transform_queue() -> client.transform_queues

* api_transform_task_count() -> len(client.transform_tasks)
* api_transform_task_head() -> client.transform_tasks.list(head=True)
* api_transform_task_get() -> client.transform_tasks.list() TO_CHECK user maybe not assigned
* api_transform_task_post() -> client.transform_tasks.add({'filename': 'test.mp4', 'media_in_id': task.media_in_id, 'profile_id': task.profile_id, 'metadata': {'title':'test by python'}, 'queue': 'transform_private'})

* api_transform_task_id_head(id) -> client.transform_tasks[id + '/HEAD']
* api_transform_task_id_get(id) -> client.transform_tasks[id] TO_CHECK user maybe not assigned
* api_transform_task_id_delete(id) -> del client.transform_tasks[id]

* api_publish_queue() -> client.publisher_queues

TO_TEST
=======

- [ ] api_publish_task_count()
- [ ] api_publish_task_head()
- [ ] api_publish_task_get() BUGGY (user is not assigned, should update Media class)
- [ ] api_publish_task_post()

- [ ] api_publish_task_id_head(id)
- [ ] api_publish_task_id_get(id) BUGGY (user is not assigned, should update TransformTask class)
- [ ] api_publish_task_id_delete(id)

- [ ] api_transform_task_hook()
- [ ] api_publish_task_hook()
- [ ] api_revoke_publish_task_hook()
