import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics import pairwise_distances


def n_neighbours(df,n):
    order = np.argsort(df.values, axis=1)[:, :n]
    df = df.apply(lambda x: pd.Series(x.sort_values(ascending=False).iloc[:n].index, index=['top{}'.format(i) for i in range(1, n+1)]), axis=1)
    return df
	
	
def similar_questions(user1, user2):
    common_questions = history_s[history_s['userID'] == user1].merge(history_s[history_s['userID'] == user2], on = "questionID", how = "inner" )
    return common_questions.merge(questions, on = 'questionID' )
	
	
def User_item_score(user,item):
    a = sim_user_m[sim_user_m.index==user].values
    b = a.squeeze().tolist()
    c = final_question.loc[:,item]
    d = c[c.index.isin(b)]
    f = d[d.notnull()]
    avg_user = userhistory.loc[userhistory['userID'] == user,'visits'].values[0]
    index = f.index.values.squeeze().tolist()
    corr = similarity_with_question.loc[user,index]
    fin = pd.concat([f, corr], axis=1)
    fin.columns = ['adg_score','correlation']
    fin['score']=fin.apply(lambda x:x['adg_score'] * x['correlation'],axis=1)
    nume = fin['score'].sum()
    deno = fin['correlation'].sum()
    final_score = avg_user + (nume/deno)
    return final_score
	
	
	
def generate_recommendations(user, n, history, questions):	

    #Normalise visits
    history['visits'] = (history['visits'] - history['visits'].min()) / (history['visits'].max() - history['visits'].min())
    userhistory = history.groupby(by='userID', as_index=False)['visits'].mean()

    history_s = pd.merge(history, userhistory, on='userID')
    history_s['norm_rating'] = history_s['visits_x'] - history_s['visits_y']
    temp = pd.pivot_table(history_s,values='visits_x',index='userID',columns='questionID')
    final = pd.pivot_table( history_s, values='norm_rating', index='userID',columns='questionID')

    #replacing by question
    final_question = final.fillna(final.mean(axis=0))

    #replacing by user average
    final_user = final.apply(lambda row: row.fillna(row.mean()), axis=1)

    # user similarity on final_user
    b = cosine_similarity(final_user)
    np.fill_diagonal(b, 0)
    similarity_with_user = pd.DataFrame(b,index=final_user.index)
    similarity_with_user.columns=final_user.index

    # user similarity on final_shop
    cosine = cosine_similarity(final_question)
    np.fill_diagonal(cosine, 0 )
    similarity_with_question = pd.DataFrame(cosine,index=final_question.index)
    similarity_with_question.columns=final_user.index


    # top n neighbours for each user and question
    sim_user_u = n_neighbours(similarity_with_user,n)
    sim_user_m = n_neighbours(similarity_with_question,n)

    history_s.userID = history_s.userID.astype(str)
    history_s.questionID = history_s.questionID.astype(str)
    question_user = history_s.groupby('userID')['questionID'].apply(lambda x:','.join(x))

    question_user.index = question_user.index.astype(int)
    question_by_user = temp.columns[temp[temp.index==user].notna().any()].tolist()
    a = sim_user_m[sim_user_m.index==user].values
    b = a.squeeze().tolist()
    d = question_user[question_user.index.isin(b)]
    l = ','.join(d.values)
    question_similar_users = l.split(',')
    questionslist = list(set(question_similar_users)-set(list(map(str, question_by_user))))
    questionslist = list(map(int, questionslist))
    score = []
    for item in questionslist:
        item = int(item)
        c = final_question.loc[:,item]
        d = c[c.index.isin(b)]
        f = d[d.notnull()]
        avg_user = userhistory.loc[userhistory['userID'] == user,'visits'].values[0]
        index = f.index.values.squeeze().tolist()
        corr = similarity_with_question.loc[user,index]
        fin = pd.concat([f, corr], axis=1)
        fin.columns = ['adg_score','correlation']
        fin['score']=fin.apply(lambda x:x['adg_score'] * x['correlation'],axis=1)
        nume = fin['score'].sum()
        deno = fin['correlation'].sum()
        final_score = avg_user + (nume/deno)
        score.append(final_score)
    data = pd.DataFrame({'questionID':questionslist,'score':score})
    recommendations = data.sort_values(by='score',ascending=False)
    questionname = recommendations.merge(questions, how='inner', on='questionID')
    
    return questionname.Name.values.tolist();