import pandas as pd
import pickle


def create_data(X):
    expanded_rows = []

    for _, row in X.iterrows():
        for day in range(row['days_left'] - 1, 0, -1):
            new_row = row.copy()
            new_row['days_left'] = day
            expanded_rows.append(new_row)
    return pd.DataFrame(expanded_rows).reset_index(drop=True)


def predict_price(path, pred_df):
    pred_with_id = create_data(pred_df)
    pred = pred_with_id.drop(columns=['flight_id', 'brand', 'price'])
    pred = pd.get_dummies(pred, columns=['destination'])

    columns_path = f"models\\columns\\{path}_columns.pkl"
    model_path = f"models\\model\\{path}_model.pkl"
    scaler_path = f"models\\scaler\\{path}_scaler.pkl"

    with open(columns_path, "rb") as f:
        feature_cols = pickle.load(f)
    pred = pred.reindex(columns=feature_cols, fill_value=0)

    with open(scaler_path, "rb") as f:
        scaler = pickle.load(f)
    scaled = scaler.transform(pred)

    with open(model_path, "rb") as f:
        model = pickle.load(f)
    predicted_price = model.predict(scaled)

    result = pred_with_id.copy()
    result['Predicted Price'] = predicted_price
    return result


def threshold_predicted(data, result):
    data = data[['flight_id', 'price']].copy()
    data['cheap_pred'] = 0

    threshold_prices = result['Predicted Price']
    n = max(1, int(0.1 * len(threshold_prices)))
    cheap_threshold = threshold_prices.nsmallest(n)
    cheap_threshold = cheap_threshold.mean()
    print(f"threshold: {cheap_threshold}")

    data.loc[data['price'] <= cheap_threshold, 'cheap_pred'] = 1
    print(data)
    return data
