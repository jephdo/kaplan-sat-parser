from . import percentiles

# for now using the percentile ranks from the original SAT 1600 test
# pre-2007
SAT_conversions = {
    "composite": percentiles.SAT_1600_COMPOSITE,
    "math": percentiles.SAT_1600_MATH,
    "reading_writing": percentiles.SAT_1600_VERBAL
}

ACT_conversions = {
    "composite": percentiles.ACT_COMPOSITE,
    "math": percentiles.ACT_MATH,
    "english": percentiles.ACT_ENGLISH,
    "reading": percentiles.ACT_READING,
    "science": percentiles.ACT_SCIENCE,
}


def dataframe_to_ranks(dataframe):
    """Given a DataFrame of raw ACT/SAT scores by composite and subject,
    convert scores into percentile ranks."""
    columns = {}
    for colname in dataframe.columns:
        if 'equivalent' in colname:
            continue
        col = dataframe[colname]
        if col.dtype == 'int64':
            col = score_to_rank(col, colname)
        columns[colname] = col
    return pd.concat(columns, axis=1).reindex(dataframe.index)


def score_to_rank(scores, subject):
    # try to infer the type of test by looking at range of scores.
    # ACT = 1-36 and SAT = 200-800
    test_type = "ACT" if scores.max() <= 36 else "SAT"
    conversions = ACT_conversions if  test_type == "ACT" else SAT_conversions
    return scores.map(conversions[subject])


def ranks_to_cdf(ranks):
    xs = pd.Series(list(range(1,100)))
    cdf = xs.map(lambda x: (ranks < x).sum())
    cdf = cdf.reindex(xs).fillna(method='ffill')
    # normalize the cdf to percentage
    return cdf / len(ranks)

