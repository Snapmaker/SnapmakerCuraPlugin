from .SnapmakerJ1Plugin import SnapmakerJ1Plugin


def getMetaData():
    return {}


def register(app):
    return {
        "extension": SnapmakerJ1Plugin()
    }
