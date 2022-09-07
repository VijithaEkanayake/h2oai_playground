import h2o_mlops_client as mlops
import requests
import json
import pandas as pd

# Create Panda data frame from scoring data csv
df = pd.read_csv("<SCORING_DATA_CSV>")


# Score using endpoint URL of a deployment
def mlops_get_score(score_url, request):
    response = requests.post(url=score_url, json=request)
    return json.loads(response.text)


# Get predictions
def get_predictions_df(score_url: str, template: dict, df: pd.DataFrame):
    col_map ={'0': float, 'text': str}
    score_cols = template['fields']
    col_types = template['rows'][0]
    tmp_df = df[score_cols]
    tmp_df = tmp_df.fillna('0')
    tmp_df = tmp_df.replace(to_replace=r'"|\'', value='', regex=True)

    for score_col, col_type in zip(score_cols, col_types):
        tmp_df[score_col] = tmp_df[score_col].astype(col_map[col_type])

    tmp_df = tmp_df.astype(str)

    request = {
        'fields': score_cols,
        'rows': tmp_df.values.tolist()
    }

    preds_response = mlops_get_score(score_url, request)
    preds_df = pd.DataFrame(data=preds_response['score'], columns=preds_response['fields'])
    return preds_df

# Create Token Provider
mlops_token_provider = mlops.TokenProvider(
    refresh_token="<REFRESH_TOKEN>",
    client_id="<CLIENT_ID>",
    token_endpoint_url="<TOKEN_ENDPOINT_URL>"
)


# Setting up MLOPS client.
mlops_client = mlops.Client(
    gateway_url="<H2O_MLOPS_GATEWAY>",
    token_provider=mlops_token_provider
)


# Get the deployment status by deployment Id
deployment_status = mlops_client.deployer.deployment_status.get_deployment_status({
    'deployment_id': "<DEPLOYMENT_ID>"
}).deployment_status

print(deployment_status.state)
print(deployment_status.scorer.sample_request.url)
print(deployment_status.scorer.score.url)

sample_request_as_text = requests.get(deployment_status.scorer.sample_request.url).text
sample_request = json.loads(sample_request_as_text)
print(sample_request)

preds = get_predictions_df(deployment_status.scorer.score.url, sample_request, df)
print(preds)