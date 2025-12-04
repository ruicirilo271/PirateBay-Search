from flask import Flask, render_template, request
import requests

app = Flask(__name__)

API_PB = "https://apibay.org/q.php"   # PirateBay oficial

@app.route("/", methods=["GET", "POST"])
def index():
    movies = []
    error = None
    query = ""

    if request.method == "POST":
        query = request.form.get("query", "").strip()

        if not query:
            error = "Insira um termo de pesquisa."
        else:
            try:
                response = requests.get(API_PB, params={"q": query}, timeout=10)

                try:
                    results = response.json()
                except:
                    error = "Erro: PirateBay não devolveu JSON válido."
                    results = []

                # Garantir que veio lista
                if isinstance(results, list):
                    for item in results:

                        # ignorar torrents sem seeders
                        if int(item.get("seeders", "0")) <= 0:
                            continue

                        name = item.get("name", "Sem título")
                        info_hash = item.get("info_hash", "")
                        size = item.get("size", "0")
                        seeders = item.get("seeders", "0")
                        leechers = item.get("leechers", "0")

                        # criar magnet link
                        magnet = (
                            f"magnet:?xt=urn:btih:{info_hash}"
                            f"&dn={name.replace(' ', '+')}"
                            f"&tr=udp://tracker.opentrackr.org:1337/announce"
                        )

                        movies.append({
                            "title": name,
                            "size": size,
                            "seeders": seeders,
                            "leechers": leechers,
                            "magnet": magnet,
                            "img": "/static/no_image.png"  # PirateBay não tem capas
                        })

                else:
                    error = "Formato inesperado recebido do PirateBay."

            except Exception as e:
                error = f"Erro ao comunicar com o PirateBay: {str(e)}"

    return render_template("index.html", movies=movies, error=error, query=query)


if __name__ == "__main__":
    app.run(debug=True)

