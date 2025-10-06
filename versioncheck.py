from re import search

def version_isold(value: str, threshold: str):
    '''バージョンをチェックする

    現在のバージョンが対象のバージョンよりも古いかどうかをチェックする
    Args:
        value(str): 現在のバージョン
        threshold(str): 対象のバージョン
    Return:
        bool: 現在のバージョンが対象のバージョンよりも古い
    '''
    if value == threshold:
        return False
    
    valueversions = value.split('.')
    thresholdversions = threshold.split('.')

    valuecount = len(valueversions)
    thresholdcount = len(thresholdversions)
    for i in range(max(valuecount, thresholdcount)):
        valuev = valueversions[i] if i < valuecount else '0'
        thresholdv = thresholdversions[i] if i < thresholdcount else '0'

        valuedev = 'dev' in valuev
        thresholddev = 'dev' in thresholdv

        if valuedev and not thresholddev:
            return True
        if not valuedev and thresholddev:
            break
        
        valuenumber = int(search(r'\d+', valuev).group())
        thresholdnumber = int(search(r'\d+', thresholdv).group())
        
        if valuenumber < thresholdnumber:
            return True
        
        if valuenumber > thresholdnumber:
            break

    return False
