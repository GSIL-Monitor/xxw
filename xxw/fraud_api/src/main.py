from src import *
from src.modules import area, event, feature, query, black_white_list, fraud_config

api.add_resource(event.EventAPI, "/query/events")
api.add_resource(event.EventCount, "/query/events_count")
api.add_resource(event.EventCountByType, "/query/events_count_by_type")
api.add_resource(feature.FeatureAPI, "/query/features")
api.add_resource(fraud_config.FraudConfigAPI, "/query/configs")
api.add_resource(area.AreaAPI, "/query/areas")
api.add_resource(query.Map, "/query/map")
api.add_resource(query.LatestMap, "/query/latest_map")
api.add_resource(query.Cycle, "/query/cycle")
api.add_resource(query.RuleTop, "/query/rules_top")
api.add_resource(black_white_list.BlackWhiteListAPI, "/query/black_white_list")
