import sys
sys.setrecursionlimit(2000)
def findLCS(matrix,x,y,i,j):
    if i == 0 or j == 0:
        return ''
    if x[i-1] == y[j-1]:
        return findLCS(matrix,x,y,i-1,j-1)+' '+x[i-1]
    if matrix[i][j-1]>matrix[i-1][j]:
        return findLCS(matrix,x,y,i,j-1)
    else:
        return findLCS(matrix,x,y,i-1,j)


def count_words_inbetween(s,lss):
    s_count = [0 for x in range(0,len(lss)+1)]

    lss_i = 0
    s_i = 0
    while(lss[lss_i]!=s[s_i]):
        s_i+=1

    s_count[0] = s_i

    lss_i+=1


    while(lss_i<len(lss)):
        tmp = s_i

        while(s_i<len(s) and lss[lss_i]!=s[s_i]):
            s_i+=1
        s_count[lss_i] = s_i-tmp-1
        lss_i+=1

    s_count[len(lss)] = len(s)-s_i-1

    return s_count

def get_longest_subsequence(s1,s2):
    s1 = s1.split(' ')
    tmp = []
    for w in s1:
        if w != '':
            tmp.append(w.strip())
    s1 = tmp

    s2 = s2.split(' ')
    tmp = []
    for w in s2:
        if w != '':
            tmp.append(w.strip())
    s2 = tmp

    m = len(s1)
    n = len(s2)

    matrix = [[0 for x in range(0,n+1)] for y in range(0,m+1)]

    # Compute the length of the longest common subsequence

    for i in range(1,m+1):
        for j in range(1,n+1):
            if s1[i-1] == s2[j-1]:
                matrix[i][j] = matrix[i-1][j-1]+1
            else:
                matrix[i][j] = max(matrix[i][j-1],matrix[i-1][j])

    res = findLCS(matrix,s1,s2,m,n)
    res = res.strip()

    if res == '':
        return None

    res_words = res.split(' ')

    # Now let's find the number of words in the original strings between each of the words
    # of the longest common subsequence    

    s1_count = count_words_inbetween(s1,res_words)
    s2_count = count_words_inbetween(s2,res_words)

    '''
    words = res.split(' ') 
    res = []
    for word in words:
        if word != '':
            res.append(word)
    res = ' '.join(res)
    '''
    return ((res,zip(s1_count,s2_count)))

