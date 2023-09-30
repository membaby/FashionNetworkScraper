from pipeline import Pipeline
import pandas as pd

if __name__ == '__main__':
    pipeline = Pipeline()
    articles = pipeline.get_articles()
    formatted_articles = []
    for article in articles:
        formatted_articles.append({
            'Article Image': article[1],
            'Article Title': article[2],
            'Description': article[4],
            'Keyword': article[3],
            'Article URL': article[0],
            'Section': article[9],
            'Action': '',
            'Article Date': article[5]
        })
    df = pd.DataFrame(articles)
    df.to_excel('articles.xlsx', index=False, header=False)