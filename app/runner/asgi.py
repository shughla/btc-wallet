from app.runner.setup import DevelopmentAppFactory

appFactory = DevelopmentAppFactory()
app = appFactory.create_app()
