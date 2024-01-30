from flask import Flask, jsonify, make_response, request
from flask_migrate import Migrate
from models import db, Hero, Power, HeroPower, HeroPowerSchema, PowerSchema

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)

db.init_app(app)

hero_power_schema = HeroPowerSchema()
power_schema = PowerSchema()

@app.route('/heroes', methods=['GET'])
def get_heroes():
    heroes = Hero.query.all()
    result = [{"id": hero.id, "name": hero.name, "super_name": hero.super_name} for hero in heroes]

    response = make_response(jsonify(result))
    response.headers['Custom-Header'] = 'SomeValue'

    return response

@app.route('/heroes/<int:hero_id>', methods=['GET'])
def get_hero(hero_id):
    hero = Hero.query.get(hero_id)
    if hero:
        result = {
            "id": hero.id,
            "name": hero.name,
            "super_name": hero.super_name,
            "powers": [
                {"id": hero_power.power.id, "name": hero_power.power.name, "description": hero_power.power.description}
                for hero_power in hero.hero_powers
            ],
        }
        return jsonify(result)
    else:
        return jsonify({"error": "Hero not found"}), 404

@app.route('/powers', methods=['GET'])
def get_powers():
    powers = Power.query.all()
    result = [power_schema.dump(power) for power in powers]
    return jsonify(result)

@app.route('/powers/<int:power_id>', methods=['GET'])
def get_power(power_id):
    power = Power.query.get(power_id)
    if power:
        result = power_schema.dump(power)
        return jsonify(result)
    else:
        return jsonify({"error": "Power not found"}), 404

@app.route('/powers/<int:power_id>', methods=['PATCH'])
def update_power(power_id):
    power = Power.query.get(power_id)
    if power:
        data = request.get_json()
        description = data.get('description')

        if description and len(description) >= 20:
            power.description = description
            db.session.commit()
            result = power_schema.dump(power)
            return jsonify(result)
        else:
            return jsonify({"errors": ["Description must be at least 20 characters long"]}), 400
    else:
        return jsonify({"error": "Power not found"}), 404

@app.route('/hero_powers', methods=['POST'])
def create_hero_power():
    data = request.get_json()
    errors = hero_power_schema.validate(data)

    if errors:
        return jsonify({"errors": errors}), 400

    hero_id, power_id, strength = data['hero_id'], data['power_id'], data['strength']
    hero = Hero.query.get(hero_id)
    power = Power.query.get(power_id)

    if not hero or not power:
        return jsonify({"error": "Hero or Power not found"}), 404

    hero_power = HeroPower(strength=strength, hero=hero, power=power)
    db.session.add(hero_power)
    db.session.commit()

    result = {
        "id": hero.id,
        "name": hero.name,
        "super_name": hero.super_name,
        "powers": [
            {"id": power.id, "name": power.name, "description": power.description}
            for power in hero.powers
        ],
    }
    return jsonify(result)

if __name__ == '__main__':
    app.run(port=3000)
