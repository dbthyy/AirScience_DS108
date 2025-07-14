import csv
import os
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for
from crawler.planetrip_crawl import crawl_planetrip, filter_user_inputs
from preprocessor.preprocessing import preprocess_planetrip
from models.predict import predict_price, threshold_predicted
app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        print(request.form.to_dict())
        destination = request.form.get("destination")
        start_day = request.form.get("start_day")
        start_hour = request.form.get("start_hour")
        brand = request.form.get("brand")
        checked_baggage = request.form.get("checked_baggage")
        if not checked_baggage:
            checked_baggage = "0"
        hand_luggage = request.form.get("hand_luggage")
        if not hand_luggage:
            hand_luggage = "0"

        file_path = "user_input.csv"
        file_exists = os.path.exists(file_path)

        with open(file_path, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)

            if not file_exists or os.stat(file_path).st_size == 0:
                writer.writerow(["brand", "hand_luggage", "checked_baggage",
                                "start_hour", "start_day", "destination"])
            writer.writerow([
                brand, hand_luggage, checked_baggage,
                start_hour, start_day, destination
            ])

        dest_code = 'SGN.' + destination
        url = f'https://www.traveloka.com/vi-vn/flight/fullsearch?ap={dest_code}&dt={start_day}.NA&ps=1.0.0&sc=ECONOMY'
        has_result_1 = crawl_planetrip(url, brand)
        has_result_2 = filter_user_inputs()
        has_result_3 = preprocess_planetrip()
        if not has_result_1 or not has_result_2 or not has_result_3:
            return redirect(url_for("go_back"))
        return redirect(url_for("result"))

    return render_template("index.html")


@app.route("/result")
def result():
    airline_logos = {
        "Vietnam Airlines": "/static/images/Vietnam_Airlines_logo.png",
        "Bamboo Airways": "/static/images/Bamboo_Airways_Logo.png",
        "VietJet Air": "/static/images/VietJet_Air_logo.png",
        "Vietravel Airlines": "/static/images/Vietravel_Airlines_Logo.png",
    }
    attributes = {
        0: "/static/images/attribute_0.png",
        1: "/static/images/attribute_1.png",
    }

    user_data = pd.read_csv("user_input.csv").iloc[0].to_dict()
    flights_df = pd.read_csv("planetrip_filtered.csv")

    X = pd.read_csv("planetrip_preprocessed.csv")
    results = []
    for brand in X['brand'].unique():
        df_brand = X[X['brand'] == brand].copy()
        if brand == 'Bamboo Airways':
            path = 'Bamboo'
        elif brand == 'Vietravel Airlines':
            path = 'Vietravel'
        elif brand == 'VietJet Air':
            path = 'Vietjet'
        elif brand == 'Vietnam Airlines':
            path = 'Vietnam'
        else:
            print(f"Không có hãng bay {brand} trong dữ liệu.")
            continue
        result = predict_price(path, df_brand)
        result = threshold_predicted(df_brand, result)
        results.append(result)
    result_df = pd.concat(results, ignore_index=True)

    flights_with_pred = flights_df.merge(
        result_df[['flight_id', 'cheap_pred']], on='flight_id', how='left')
    print(flights_with_pred)
    flights_with_pred = flights_with_pred.to_dict(orient='records')

    return render_template("result.html", user_data=user_data, flights=flights_with_pred, airline_logos=airline_logos, attributes=attributes)


@app.route("/buy-now")
def buy_now():
    return "<h1>Buy Now</h1>"


@app.route("/return")
def go_back():
    return "<h1>Không có chuyến bay nào phù hợp với yêu cầu của bạn.</h1>"


@app.route("/")
def go_to_result():
    return redirect(url_for("result"))


if __name__ == '__main__':
    app.run(debug=True)
