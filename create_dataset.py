import re

import pandas as pd
from scipy.stats import fisher_exact


def categorize_opinion(title_text: str) -> str:
    """Categorize opinion types based on their title text.

    Args:
        title_text (str): Title text of an opinion.

    Returns:
        str: fixed string categorizing the opinion (PARTLY, DISSENTING, CONCURRING, OPINION). Default is UNKOWN.
    """
    if re.findall(r"PARTLY", title_text, re.I):
        return "PARTLY"
    if re.findall(r"DISSENTING", title_text, re.I):
        return "DISSENTING"
    if re.findall(r"CONCURRING", title_text, re.I):
        return "CONCURRING"
    if re.findall(r"OPINION", title_text, re.I):
        return "OPINION"
    else:
        return "UNKNOWN"


def create_dataframe(
    df_webcasts: pd.DataFrame,
    df_announced: pd.DataFrame,
    df_reported: pd.DataFrame,
    df_questions: pd.DataFrame,
    df_opinions: pd.DataFrame,
) -> pd.DataFrame:
    """ Create the dataset questions and opinions from the previously loaded dataframes holding the required information.

    Args:
        df_webcasts (pd.DataFrame): Dataframe containing relevant webcasts
        df_announced (pd.DataFrame): Dataframe containing all announced judges in press releases
        df_reported (pd.DataFrame): Dataframe containing all reported judges in judgment documents
        df_questions (pd.DataFrame): Dataframe containing all questions extracted from hearing transcripts
        df_opinions (pd.DataFrame): Dataframe containing all opinions extracted from judgment documents

    Returns:
        pd.DataFrame: Dataframe with all participants of all hearings (attending both) with a corresponding (or lack of) question and opinion
    """
    values = []
    columns = [
        "webcast_id",
        "name",
        "has_question",
        "has_opinion",
        "language",
        "question",
        "case_id",
        "opinion",
        "opinion_type",
    ]
    for _, r in df_webcasts.iterrows():
        # select current webcast id
        w_id = r["webcast_id"]
        # select all relevant rows from the dfs
        announced = df_announced.loc[df_announced["webcast_id"] == w_id, "listed"]
        reported = df_reported.loc[df_reported["webcast_id"] == w_id, "listed"]
        set_announced = set(announced.iloc[0].split(","))
        set_reported = set(reported.iloc[0].split(","))
        # participants are only people present in announcement and judgment!
        participants = set_announced.intersection(set_reported)
        questions = df_questions.loc[
            df_questions["webcast_id"] == w_id, ["name", "text", "lang"]
        ]
        opinions = df_opinions.loc[
            df_opinions["webcast_id"] == w_id, ["opinions", "case_id"]
        ].iloc[0]
        # iterate through all participants in the current webcast
        for p in participants:
            # participant has a question
            q = p in questions.values
            # participant has an opinion
            o = p in opinions["opinions"].keys()
            question_text = (
                questions.loc[questions["name"] == p, "text"].iloc[0] if q else ""
            )
            lang = questions.loc[questions["name"] == p, "lang"].iloc[0] if q else "en"
            case_id = opinions["case_id"]
            opinion_text = opinions["opinions"][p] if o else ""
            opinion_type = categorize_opinion(opinions["opinions"][p][0]) if o else ""
            entry = [w_id, p, q, o, lang, question_text, case_id, opinion_text, opinion_type]
            values.append(entry)
    # create df from extracted values
    df_qando = pd.DataFrame(data=values, columns=columns)

    return df_qando


def fisher_test(df_qando: pd.DataFrame) -> None:
    """ Conduct the exact Fisher test on the question and opinion dataset.
        Calculations are based on the fields "has_question" and "has_opinion".
    Args:
        df_qando (pd.DataFrame): Dataframe containing the question and opinion dataset.
    """
    # Cross tabulation between hasQuestion and hasOpinion
    crosstab_result = pd.crosstab(
        index=df_qando["has_question"], columns=df_qando["has_opinion"]
    )

    # performing fishers exact test on the data
    odd_ratio, p_value = fisher_exact(crosstab_result, alternative="two-sided")
    print(f"Exact Fisher test odd ratio is : {odd_ratio:10.8f}")
    print(f"Exact Fisher test P-Value is : {p_value:10.8f}")


def load_json_files(
    fwebcasts: str = "selected_webcasts.json",
    fquestions: str = "dataset_judge_questions.json",
    fannounced: str = "judges_from_press.json",
    freported: str = "judges_from_judgments.json",
    fopinions: str = "opinions_from_judgments.json",
) -> (pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame):
    """ Loads the json files containing all required infos into dataframes for easier processing.

    Args:
        fwebcasts (str, optional): Location of the webcast file. Defaults to "selected_webcasts.json".
        fquestions (str, optional): Location of the question file. Defaults to "dataset_judge_questions.json".
        fannounced (str, optional): Location of the announced judges file. Defaults to "judges_from_press.json".
        freported (str, optional): Location of the reported judges file. Defaults to "judges_from_judgments.json".
        fopinions (str, optional): Location of the opinions file. Defaults to "opinions_from_judgments.json".

    Returns:
        pd.DataFrame: Dataframe containing selected webcasts.
        pd.DataFrame: Dataframe containing announced judges.
        pd.DataFrame: Dataframe containing reported judges.
        pd.DataFrame: Dataframe containing questions asked.
        pd.DataFrame: Dataframe containing opinions from judgments.
    """
    # load dataframes
    df_selected_webcasts = pd.read_json(fwebcasts, dtype={"webcast_id": str})
    df_questions = pd.read_json(fquestions, dtype={"webcast_id": str})
    df_judges_announced = pd.read_json(fannounced, dtype={"webcast_id": str})
    df_judges_reported = pd.read_json(freported, dtype={"webcast_id": str})
    df_separate_opinions = pd.read_json(fopinions, dtype={"webcast_id": str})
    # transform judges in announced into list
    df_judges_announced["listed"] = df_judges_announced["judges"].apply(
        lambda x: ",".join(x.values())
    )
    # homogenize dates
    df_separate_opinions["hearing_date"] = pd.to_datetime(
        df_separate_opinions["hearing_date"], unit="ms"
    )
    df_judges_reported["hearing_date"] = pd.to_datetime(
        df_judges_reported["hearing_date"], unit="ms"
    )
    # select only opinions relevant for webcast selection
    df_separate_opinions = df_separate_opinions.loc[
        df_separate_opinions["webcast_id"].isin(df_selected_webcasts["webcast_id"])
    ]

    return (
        df_selected_webcasts,
        df_judges_announced,
        df_judges_reported,
        df_questions,
        df_separate_opinions,
    )


if __name__ == "__main__":
    # load the relevant data into dataframes
    df_webcasts, df_announced, df_reported, df_questions, df_opinions = load_json_files(
        "selected_webcasts.json",
        "dataset_judge_questions.json",
        "judges_from_press.json",
        "judges_from_judgments.json",
        "opinions_from_judgments.json",
    )
    df_opinions_questions = create_dataframe(
        df_webcasts, df_announced, df_reported, df_questions, df_opinions
    )
    # save the questions and opinions dataset to a new json file
    df_opinions_questions.to_json("dataset_questions_opinions.json")
    # conduct the exact Fisher test on the dataset
    fisher_test(df_opinions_questions)
