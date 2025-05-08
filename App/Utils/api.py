import os
import json
import boto3
import hmac
import base64
import hashlib
import requests

from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from pprint import pprint
from botocore.exceptions import ClientError


os.environ["COGNITO_CLIENT_SECRET"] = (
    "11181idr8ho95i6k67v99p3go2sn72kri5j5qdg2lo4jl0uj9ri4"
)
os.environ["COGNITO_PASSWORD"] = "Ashutosh@LLM@56"
os.environ["COGNITO_USERNAME"] = "ashudhopte123@gmail.com"
os.environ["COGNITO_USER_POOL_ID"] = "us-east-1_7Rq8X1q2q"
os.environ["COGNITO_CLIENT_ID"] = "7v15em5a0iqvb3hn5r69cg3485"


def calculate_secret_hash(username, client_id, client_secret):
    message = username + client_id
    dig = hmac.new(
        key=client_secret.encode("utf-8"),
        msg=message.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).digest()
    return base64.b64encode(dig).decode()


def get_cognito_token():
    try:
        # Initialize Cognito Identity Provider client
        client = boto3.client("cognito-idp", region_name="us-east-1")

        # Get credentials from environment variables
        client_id = os.environ.get("COGNITO_CLIENT_ID")
        client_secret = os.environ.get("COGNITO_CLIENT_SECRET")
        username = os.environ.get("COGNITO_USERNAME")
        password = os.environ.get("COGNITO_PASSWORD")

        # Calculate secret hash
        secret_hash = calculate_secret_hash(username, client_id, client_secret)

        # Initiate auth flow
        response = client.initiate_auth(
            ClientId=client_id,
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={
                "USERNAME": username,
                "PASSWORD": password,
                "SECRET_HASH": secret_hash,  # Use the calculated secret hash here
            },
        )

        return {
            "status": 200,
            "access_token": response["AuthenticationResult"]["AccessToken"],
        }

    except ClientError as e:
        return {"status": 500, "message": str(e)}


litellm_proxy_endpoint = os.environ.get(
    "litellm_proxy_endpoint", "https://api-llm.ctl-gait.clientlabsaft.com"
)
temperature = 0
max_tokens = 4096
bearer_token = get_cognito_token()["access_token"]
x_api_key = "Bearer sk-vECQBNrV434Z5vmW1dhg6w"


def discoverAllModels():

    url = f"{litellm_proxy_endpoint}/model/info"

    payload = ""
    headers = {"Authorization": f"Bearer {bearer_token}", "x-api-key": x_api_key}

    response = requests.request(
        "GET", url, headers=headers, data=payload, verify=True
    )  #'cacert.pem')

    print(json.loads(response.text))


CHOSEN_LITE_LLM_MODEL = "Anthropic Claude-V3.5 Sonnet Vertex AI (Internal)"

chat = ChatOpenAI(
    openai_api_base=litellm_proxy_endpoint,  # set openai_api_base to the LiteLLM Proxy
    model=CHOSEN_LITE_LLM_MODEL,
    default_headers={"x-api-key": x_api_key},
    temperature=temperature,
    api_key=bearer_token,
    streaming=False,
    user=bearer_token,
)


def getDataTypes(input_json):

    some_content = f"""
        {input_json}

        Above is the json data of the mulitple tables, 'number_of_rows' which is not a column, rest of the key are columns and values of their first row. 
        Analyze the data and give the output in the form of following format.
        Also give purpose and target audience based on the table name, columns and the values.
        DO NOT CHANGE THE NAME OF THE TABLES AND COLUMNS.
        And only give the output json, no other sentences and explainations, such that I can parse the output directly using json.dumps.
    
    """

    some_content = (
        some_content
        + """
        {   'tables': {
                'table_name_1': {
                    'description': 'short description',
                    'columns': {
                        'column_name_1': {
                            'datatype': 'dataType, eg. int, float, string, etc.',
                            'description': 'short description',
                            'isIdentifier': true,
                            'isCategorical': 'true/false, eg. age is not catgorical but offer_type is',
                            'isDate': 'false/true',
                            'dateFormat': 'format, eg. YYYYMMDD, MMDDYYYY, MM-DD-YYYY',
                            'isArray': 'true/false',
                            'isJson': 'true/false
                        }
                    }
                }
            },
            'purpose': 'short sentence',
            'targetAudience': 'comma separated values'
        }
        """
    )

    messages = [
        SystemMessage(
            content="You are a instruction-tuned large language model. Follow the user's instructions carefully. Respond using markdown."
        ),
        HumanMessage(content=some_content),
    ]

    try:
        response = chat(messages)

        # pprint(response.content)

        # outputJson = response

        # outputJson = json.dumps(outputJson["content"].strip("```json").strip("```"))

    except Exception as e:
        json_str = str(e).split(" - ", 1)[1]
        print(eval(json_str)["error"]["message"])

    return response.content


def getJoins(input_json):

    some_content = f"""
        {input_json}

        Above is the json data of the multiple tables, their columns and unique values.
        The 'values' here is conditional:
            1. If the column is identifier or (is string and not categorical), then it will be first 5 values
            2. If the column is not identifier, is string, and is categorical, then it will have all the unique values
            3. If the columns is not identifier and is not string, then just first 5 values
        It also has MIN_VALUE and MAX_VALUE, which will be only for the columns which are not identifier and is integer.
        So, for the integer columns, based on the column and the min-max values, you have to find the OUTLIERS.
        And for the string columns, based on the columns and values, you have to find the OUTLIERS within them.
        The Outliers should only be mentioned if they seems serious, moderate outliers are okay.
        In the description, write about the Dataset, it's tables and relations, it's possible usage, and insights it may provide.
        And the main thing, find the JOIN relation between these tables and columns, in the following JSON format.
        DO NOT CHANGE THE NAME OF THE TABLES AND COLUMNS.
        And only give the output json, no other sentences and explainations, such that I can parse the output directly using json.dumps.
    
    """

    some_content = (
        some_content
        + """
        {
            'joins' :[
                {
                    'table_1': 'table_name',
                    'table_2': 'table_name',
                    'column_1': 'column_name_of_table_1',
                    'column_2': 'column_name_of_table_2',
                    'column_1_relation': 'one/many',
                    'column_2_relation': 'one/many'
                }
            ],
            'outliers':{
                'table_1':{
                    'column_1': {
                        'isOutlier': 'false/true',
                        'outlier_reason': 'small sentence',
                        'outlier_values': ['value_1', 'value_2'],
                        'valid_min_value': 'MIN_NUMBER',
                        'valid_max_value': 'MAX_NUMBER'
                    }
                }
            }
        },
        "description": "Detailed description about the entire dataset here in printable string format"
        """
    )

    messages = [
        SystemMessage(
            content="You are a instruction-tuned large language model. Follow the user's instructions carefully. Respond using markdown."
        ),
        HumanMessage(content=some_content),
    ]

    try:
        response = chat(messages)

    except Exception as e:
        json_str = str(e).split(" - ", 1)[1]
        print(eval(json_str)["error"]["message"])

    return response.content


def getPlots(dataTypeJson, joinJson):

    some_content = f"""

        Below is the data containing all the tables, columns and respective metadata.
        {dataTypeJson}

        Below is the data containing the relations betwen the tables and columns, and the outliers values
        {joinJson}

        Analyze the above 2 json data and give me the possible pair of columns using which I can plot chart in plotly.
        Also suggest the plot type, and its business insights.
        Look at the datatypes of the columns carefully and suggest graphs that can be plotted accordinly.
        value_columns are the columns which are the understandable values of the foreign key column, eg. in the one-to-many relation, the 'many' column might be id, but on its original table is assigned to a understandable value such as offer_type.
        Make sure to give the output based on the importance of the data and whether it has any business value.
        Use the below JSON format to give the output.
        DO NOT CHANGE THE NAME OF THE TABLES AND COLUMNS.
        And only give the output json, no other sentences and explainations, such that I can parse the output directly using json.dumps.
    
    """

    some_content = (
        some_content
        + """
        [
            {
                'table_1': 'table_name',
                'table_2': 'table_name',
                'column_1': 'column name of table_1',
                'column_2': 'column name of table_2',
                'value_column_1': 'column name which has the understandable value corresponding to the foreign key columns_1',
                'value_column_2': 'column name which has the understandable value corresponding to the foreign key columns_2',
                'plot_type': 'line/bar/pie/box/heatmap/histogram/etc.',
                'business_insight': 'short description'
            }
        ]
        """
    )

    messages = [
        SystemMessage(
            content="You are a instruction-tuned large language model. Follow the user's instructions carefully. Respond using markdown."
        ),
        HumanMessage(content=some_content),
    ]

    try:
        response = chat(messages)

    except Exception as e:
        json_str = str(e).split(" - ", 1)[1]
        print(eval(json_str)["error"]["message"])

    return response.content


# if __name__ == "__main__":
#     getDataTypes()
