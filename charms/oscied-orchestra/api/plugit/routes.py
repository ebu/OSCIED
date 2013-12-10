from params import PI_BASE_URL
from views import *

def load_routes(app,actions):

    @app.route(PI_BASE_URL + "ping")
    def ping():
        """The ping method: Just return the data provided"""
    
        if not check_ip(request):
            return
    
        return jsonify(data=request.args.get('data', ''))
    
    
    @app.route(PI_BASE_URL + "version")
    def version():
        """The version method: Return current information about the version"""
        return jsonify(result='Ok', version=PI_API_VERSION, protocol=PI_API_NAME)


    @app.route(PI_BASE_URL + "mail", methods=['POST'])
    def mail():
        """The mail method: Process mail handling"""

        data = request.form['response_id'].split(':')

        if data[0] == 'dis':

            discussion = Discussion.query.filter(Discussion.id == int(data[1])).first()
            if discussion.is_closed:
                api.send_mail('', 'Error', [api.get_user(data[2]).email], 'You tried to reply to the discussion ' + discussion.title + ' but the discussion is closed.\n\nBests,')

                return jsonify(result='Ok')

            post = DiscussionPost()
            post.discussion_id = int(data[1])
            post.author = int(data[2])
            post.date = datetime.now()
            post.message = request.form['message']

            db.session.add(post)
            db.session.commit()

            post.send_mail()
            
        return jsonify(result='Ok')
    
    # Register the 3 URLs (meta, template, action) for each actions
    # We test for each element in the module actions if it's an action
    # (added by the decorator in utils)
    for act in dir(actions):
        obj = getattr(actions, act)
        if hasattr(obj, 'pi_api_action') and obj.pi_api_action:
            # We found an action and we can now add it to our routes
            
            # Meta
            app.add_url_rule(
                PI_BASE_URL + 'meta' + obj.pi_api_route,
                view_func=MetaView.as_view('meta_' + act, action=obj))
    
            # Template
            app.add_url_rule(
                PI_BASE_URL + 'template' + obj.pi_api_route,
                view_func=TemplateView.as_view('template_' + act, action=obj))
    
            # Action
            app.add_url_rule(
                PI_BASE_URL + 'action' + obj.pi_api_route,
                view_func=ActionView.as_view('action_' + act, action=obj),
                methods=obj.pi_api_methods)
