import instaloader
import pandas as pd
import unidecode
import re
import getpass
import os

def get_comments(post_shortcode, L) -> pd.DataFrame:
    post = instaloader.Post.from_shortcode(L.context, post_shortcode)

    comments = []
    for comment in post.get_comments():
        comment_data = {
            'username': comment.owner.username,
            'comment': comment.text,
            'comment_date': comment.created_at_utc,
            'shortcode': post_shortcode,
            'post_date': post.date
        }
        comments.append(comment_data)
    return pd.DataFrame(comments)

def extract_bet(comment: str) -> str:
    pattern = r"(\d+\s*x\s*\d+)\s*(\w+)"
    match = re.search(pattern, comment)
    if match:
        return f"{match.group(1).replace(' ', '')} {match.group(2)}"
    else:
        return None

def normalize_string(s: str) -> str:
    if isinstance(s, str):
        return unidecode.unidecode(s).lower()
    return s

def split_numbers_text(s: str):
    if not isinstance(s, str):
        return '', ''
    numbers = re.findall(r'\d+', s)
    numbers = ''.join(numbers)
    text = re.sub(r'\d+', '', s).strip()
    text = normalize_string(text)
    return numbers, text

def combine_components(numbers: str, text: str) -> str:
    return f"{numbers} {text}".strip()

def validate_bet(row: pd.Series, bet_column="bet", result_column="result", comment_column="comment") -> bool:
    bet = row[bet_column]
    expected_result = row[result_column]
    comment = row[comment_column]

    if bet is None:
        comment_numbers, comment_text = split_numbers_text(comment)
        result_numbers, result_text = split_numbers_text(expected_result)
        normalized_comment = combine_components(comment_numbers, comment_text)
        normalized_result = combine_components(result_numbers, result_text)
        return normalized_comment == normalized_result
    else:
        bet_numbers, bet_text = split_numbers_text(bet)
        result_numbers, result_text = split_numbers_text(expected_result)
        normalized_bet = combine_components(bet_numbers, bet_text)
        normalized_result = combine_components(result_numbers, result_text)
        return normalized_bet == normalized_result

if __name__ == "__main__":
    data = pd.DataFrame()

    username = input("Enter your Instagram username: ")
    password = getpass.getpass("Enter your Instagram password: ")

    L = instaloader.Instaloader()
    L.login(username, password)

    input_data = pd.read_csv('input.csv')

    try:
        # Loop through each day and collect all comments
        for day in input_data["Day"].unique():
            input_temp = input_data[input_data["Day"] == day]
            shortcodes = input_temp['shortcode']
            for post in shortcodes:
                comments = get_comments(post, L)
                data = pd.concat([data, comments], ignore_index=True)

    except Exception as e:
        print(f"An error occurred: {e}")
        print("Saving progress before exiting...")
        if not data.empty:
            data.to_csv(f"data_all_days_progress.csv", index=False)
        raise

    # Save final data after completing the loop
    data.to_csv(f"data_all_days.csv", index=False)

    df = data.merge(input_data, on='shortcode', how='left')
    df['bet'] = df['comment'].apply(extract_bet)
    df['bet_result'] = df.apply(validate_bet, axis=1)
    df.drop_duplicates(inplace=True)
    df.to_csv('data.csv', index=False)
    print(df)

    leaderboard = df.groupby('username')['bet_result'].apply(lambda x: x[x == True].count()).reset_index(name='score')
    leaderboard = leaderboard.sort_values(by='score', ascending=False).reset_index(drop=True)
    leaderboard.to_csv('leaderboard.csv', index=False)
    print(leaderboard)
