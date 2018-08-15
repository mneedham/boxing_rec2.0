from flask import Flask, render_template, send_from_directory
from neo4j.v1 import GraphDatabase

app = Flask(__name__, static_url_path="")
driver = GraphDatabase.driver("bolt://localhost", auth=("neo4j", "abc"))


@app.route("/")
def hello_world():
    return "Hello World!"


@app.route("/fighters")
def fighters():
    with driver.session() as session:
        result = session.run("""\
        MATCH (winner:Boxer)-[:BEAT]->(loser)
        RETURN winner, loser

        """)
        boxers = [
            {
                "winner": row["winner"],
                "loser": row["loser"],
            }
            for row in result]

        result = session.run("""\
        MATCH (winner:Boxer)-[:POTENTAIL_FIGHT]->(loser)
        RETURN winner, loser
        """)
        potential_fights = [
            {
                "winner": row["winner"],
                "loser": row["loser"],
            }
            for row in result]

    return render_template("scratch.html", boxers=boxers, potential_fights=potential_fights)

@app.route("/fighters/<name>")
def fighter(name):
    with driver.session() as session:
        result = session.run("""\
        MATCH (boxer:Boxer {name: $name})-[beat:BEAT]-(opponent)
        RETURN CASE WHEN startNode(beat) = boxer THEN boxer ELSE opponent END AS winner,
               CASE WHEN endNode(beat) = boxer THEN boxer ELSE opponent END AS loser
        """, {"name": name})
        boxers = [
            {
                "winner": row["winner"],
                "loser": row["loser"],
            }
            for row in result]

        result = session.run("""\
        MATCH (boxer:Boxer {name: $name})-[beat:BEAT]-(opponent)
        RETURN CASE WHEN startNode(beat) = boxer THEN boxer ELSE opponent END AS winner,
               CASE WHEN endNode(beat) = boxer THEN boxer ELSE opponent END AS loser
        """, {"name": name})
        potential_fights = [
            {
                "winner": row["winner"],
                "loser": row["loser"],
            }
            for row in result]

    return render_template("scratch.html", boxers=boxers, potential_fights=potential_fights)

@app.route("/fighters/<boxer1>/<boxer2>")
def fight (boxer1,boxer2):
    with driver.session() as session:
        result = session.run("""\
        MATCH (boxer:Boxer {name: $boxer1})-[beat:BEAT]-(opponent {name: $boxer2}) 
        RETURN CASE WHEN startNode(beat) = boxer THEN boxer ELSE opponent END AS winner,
               CASE WHEN endNode(beat) = boxer THEN boxer ELSE opponent END AS loser,
               beat.highlights as video
        """, {"boxer1": boxer1, "boxer2": boxer2})
        boxers = [
            {
                "winner": row["winner"],
                "loser": row["loser"],
                "video": row["video"]
            }
            for row in result]

    return render_template("fight.html", boxers=boxers)
















if __name__ == "__main__":
    app.run(debug=True)
