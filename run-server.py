import sys
import uvicorn.workers

from configurations.environments import Values

app = "configurations.main:app"

if __name__ == "__main__":
    if "--reload" in sys.argv:
        # Running with uvicorn in development mode (with --reload)
        uvicorn.run(app, host="0.0.0.0", port=8005, workers=2, reload=True)
    else:
        # Running with gunicorn in production mode

        class MyUvicornWorker(uvicorn.workers.UvicornWorker):
            def handle_exit(self, sig, frame):
                # Handle worker exit to close the database connection cleanly
                self.app.setup.shutdown()
                super().handle_exit(sig, frame)


        allowed_ips = [ip for ip in Values.FORWARDED_ALLOW_IPS.split(',')]
        uvicorn.run(app, host="0.0.0.0", port=8005, workers=Values.Workers, reload=False)
