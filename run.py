import os
from app import create_app, socketio

app = create_app()

if __name__ == '__main__':
    print("=========================================================")
    print(" EcoRoute AI - Smart Society Waste Management System ")
    print(" Running at: http://127.0.0.1:5000 ")
    print(" Motto: 'Smarter Routes. Cleaner Communities.'")
    print("=========================================================")

    # NOTE: This __main__ block is for LOCAL DEVELOPMENT only
    # (`python run.py`). For production deployment, run via Gunicorn with
    # the eventlet worker instead (see DEPLOYMENT.md) - Gunicorn imports
    # the `app` object above directly and never executes this block, so
    # debug mode / the Werkzeug dev server are never used in production.
    debug_mode = os.environ.get('FLASK_DEBUG', 'True') == 'True'
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=debug_mode, allow_unsafe_werkzeug=debug_mode)
