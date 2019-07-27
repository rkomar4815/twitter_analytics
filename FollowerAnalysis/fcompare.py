import pandas as pd

#  This section compares followers to following users

A = pd.read_csv('3_28_19 NatSecAction Following.csv', index_col=0)
print(A)

B = pd.read_csv('3_28_19 NatSecAction Followers.csv', index_col=0)
print(B)

C = pd.merge(
    left=A, right=B,
    how='outer', left_index=True,
    right_index=True, suffixes=['_a', '_b']
    )

print(C)

not_in_a = C.drop(A.index)
not_in_b = C.drop(B.index)

not_in_a.to_csv('not_in_a.csv')
not_in_b.to_csv('not_in_b.csv')

D = pd.read_csv('not_in_b.csv')
E = pd.read_csv('not_in_a.csv')


a_notin_b = len(D.index)
print(
    'Number of accounts you follow that do not follow back: '
    + str(a_notin_b)
    )

a_total = len(A.index)
print(
    'The total number of accounts that you follow: '
    + str(a_total)
    )

nonfollowbackratio = (a_notin_b/a_total)*100
percent_nonfollowback = str(nonfollowbackratio) + '%'
print(
    'Percent of accounts that you follow that do not follow back: '
    + str(percent_nonfollowback)
    )

#  This section identifies ranks followers by their followers

sortedE = E.sort_values(by=['followers_count_b'], ascending=False)

E_columns_to_remove = [
    'id_str_a', 'name_a', 'location_a', 'description_a',
    'created_at_a', 'url_a', 'verified_a', 'lang_a',
    'friends_count_a', 'followers_count_a', 'statuses_count_a',
    'favourites_count_a', 'last_tweeted_at_a', 'id_str_b',
    'location_b', 'created_at_b', 'url_b', 'lang_b',
    '_count_b', 'last_tweeted_at_b', 'name_b',
    'statuses_count_b'
    ]

print(sortedE.columns)

sortedE2 = sortedE.drop(columns=E_columns_to_remove)

print(sortedE2.columns)

sortedE2.to_csv('sorted_natesecationfollowers_by_followcount.csv')
