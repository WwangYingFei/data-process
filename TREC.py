# !/usr/bin/python
# encoding=utf8
import re
from xml.dom.minidom import parse
import xml.dom.minidom
import sys
sys.path.append("..")
import argparse
import numpy as np
from utils import *
import random

def generate_dict_list(args):
    punc = '\\~`!#$%^&*()_+-=|\';":/.,?><~·！@#￥%……&*（）——+-=“：’；、。，？》《{}'
    session_sid = {}
    query_qid, url_uid, vtype_vid = {'': 0}, {'': 0}, {'': 0}
    uid_description = {}
    total_click_num = 0

    print('  - {}'.format('start parsing xml file...'))
    DOMTree = xml.dom.minidom.parse(os.path.join(args.input, args.dataset))
    TREC2014 = DOMTree.documentElement
    sessions = TREC2014.getElementsByTagName('session')

    # generate infos_per_session
    print('  - {}'.format('generating infos_per_session...'))
    infos_per_session = []
    junk_interation_num = 0
    for session in sessions:
        info_per_session = {}
        # get the session id
        session_number = int(session.getAttribute('num'))
        if not (session_number in session_sid):
            session_sid[session_number] = len(session_sid)
        info_per_session['session_number'] = session_number
        info_per_session['sid'] = session_sid[session_number]
        # print('session: {}'.format(session_number))

        # Get topic id
        topic = int(session.getElementsByTagName('topic')[0].getAttribute('num'))
        info_per_session['topic'] = topic

        # Get information within a query
        interactions = session.getElementsByTagName('interaction')
        interaction_infos = []
        for interaction in interactions:
            interaction_info = {}

            # Get query/document infomation
            query = interaction.getElementsByTagName('query')[0].childNodes[0].data
            remove_chars = '[-_——...|、“”！!？，：（）()?\\│#「」,<>。【】×》《$]+'
            content = re.sub(remove_chars, " ", query)
            pattern = re.compile("[^\u4e00-\u9fa5^a-z^A-Z^0-9]")  
            line = re.sub(pattern, ' ', content)  
            query = ''.join(line) 
            # print(query)
            docs = interaction.getElementsByTagName('results')[0].getElementsByTagName('result')
            doc_infos = []

            # Sanity check
            if len(docs) == 0:
                print('  - {}'.format('WARNING: find a query with no docs: {}'.format(query)))
                junk_interation_num += 1
                continue
            elif len(docs) > 10:
                # more than 10 docs is not ok. May cause index out-of-range in embeddings
                print('  - {}'.format('WARNING: find a query with more than 10 docs: {}'.format(query)))
                junk_interation_num += 1
                continue
            elif len(docs) < 10:
                # less than 10 docs is ok. Never cause index out-of-range in embeddings
                print('  - {}'.format('WARNING: find a query with less than 10 docs: {}'.format(query)))
                junk_interation_num += 1
                continue

            # Pass the sanity check, save useful information
            if not (query in query_qid):
                query_qid[query] = len(query_qid)
            interaction_info['query'] = query
            interaction_info['qid'] = query_qid[query]
            interaction_info['session'] = info_per_session['session_number']
            interaction_info['sid'] = info_per_session['sid']

            for doc_idx, doc in enumerate(docs):
                # WARNING: In case there might be junk data in TREC2014 (e.g., rank > 10),  so we use manual doc_rank here
                # NOTE: Vertical type is not provided in TREC datasets. It is now only provided in demo.
                #       So we manually set vtype equal to 0, whose corresponding qid is 1.
                doc_rank = int(doc.getAttribute('rank'))
                doc_rank = 10 if doc_rank % 10 == 0 else doc_rank % 10
                assert 1 <= doc_rank and doc_rank <= 10
                assert doc_idx + 1 == doc_rank
                url = doc.getElementsByTagName('clueweb12id')[0].childNodes[0].data
                doc_title = doc.getElementsByTagName('title')[0].childNodes[0].data
                remove_chars = '[-_——...|、“”！!？，：（）()?\\│#「」,<>。【】×》《$]+'
                content = re.sub(remove_chars, " ", doc_title)
                pattern = re.compile("[^\u4e00-\u9fa5^a-z^A-Z^0-9]")  
                line = re.sub(pattern, ' ', content)  
                doc_title = ''.join(line)  
                # print(doc_title)
                vtype = '0'
                if not (url in url_uid):
                    url_uid[url] = len(url_uid)
                if not (vtype in vtype_vid):
                    vtype_vid[vtype] = len(vtype_vid)
                doc_info = {}
                doc_info['rank'] = doc_rank
                doc_info['url'] = url
                doc_info['uid'] = url_uid[url]
                doc_info['doc_title'] = doc_title
                doc_info['vtype'] = vtype
                doc_info['vid'] = vtype_vid[vtype]
                doc_info['click'] = 0
                doc_infos.append(doc_info)
                # print('      doc ranks at {}: {}'.format(doc_rank, url))

            # Get click information if there are clicked docs
            # Maybe there are no clicks in this query
            clicks = interaction.getElementsByTagName('clicked')
            if len(clicks) > 0:
                clicks = clicks[0].getElementsByTagName('click')
                total_click_num += len(clicks)
                for click in clicks:
                    clicked_doc_rank = int(click.getElementsByTagName('rank')[0].childNodes[0].data)
                    for item in doc_infos:
                        if item['rank'] == clicked_doc_rank:
                            item['click'] = 1
                            break
                    # print('      click doc ranked at {}'.format(clicked_doc_rank))
            else:
                pass
                # print('      click nothing')
            interaction_info['docs'] = doc_infos
            # print(doc_infos)
            interaction_info['uids'] = [doc['uid'] for doc in doc_infos]
            interaction_info['docs'] = [doc['doc_title'] for doc in doc_infos]
            interaction_info['vids'] = [doc['vid'] for doc in doc_infos]
            interaction_info['clicks'] = [doc['click'] for doc in doc_infos]
            interaction_infos.append(interaction_info)
        info_per_session['interactions'] = interaction_infos
        # print(info_per_session)
        infos_per_session.append(info_per_session)
        # print(infos_per_session)
    print('  - {}'.format('abandon {} junk interactions'.format(junk_interation_num)))

    # generate infos_per_query
    print('  - {}'.format('generating infos_per_query...'))
    infos_per_query = []
    for info_per_session in infos_per_session:
        interaction_infos = info_per_session['interactions']
        for interaction_info in interaction_infos:
            infos_per_query.append(interaction_info)

    # save and check infos_per_session
    print('  - {}'.format('save and check infos_per_session...'))
    print('    - {}'.format('length of infos_per_session: {}'.format(len(infos_per_session))))
    # pprint.pprint(infos_per_session)
    # print('length of infos_per_session: {}'.format(len(infos_per_session)))
    save_list(args.output, 'infos_per_session.list', infos_per_session)
    list1 = load_list(args.output, 'infos_per_session.list')
    assert len(infos_per_session) == len(list1)
    for idx, item in enumerate(infos_per_session):
        assert item == list1[idx]

    # save and check infos_per_query
    print('  - {}'.format('save and check infos_per_query...'))
    print('    - {}'.format('length of infos_per_query: {}'.format(len(infos_per_query))))
    # pprint.pprint(infos_per_query)
    # print('length of infos_per_query: {}'.format(len(infos_per_query)))
    save_list(args.output, 'infos_per_query.list', infos_per_query)
    list2 = load_list(args.output, 'infos_per_query.list')
    assert len(infos_per_query) == len(list2)
    for idx, item in enumerate(infos_per_query):
        assert item == list2[idx]

    # save and check dictionaries
    print('  - {}'.format('save and check dictionaries...'))
    print('    - {}'.format('unique session number: {}'.format(len(session_sid))))
    print('    - {}'.format('unique query number: {}'.format(len(query_qid))))
    print('    - {}'.format('unique doc number: {}'.format(len(url_uid))))
    print('    - {}'.format('unique vtype number: {}'.format(len(vtype_vid))))
    print('    - {}'.format('total click number: {}'.format(total_click_num)))
    save_dict(args.output, 'session_sid.dict', session_sid)
    save_dict(args.output, 'query_qid.dict', query_qid)
    save_dict(args.output, 'url_uid.dict', url_uid)
    save_dict(args.output, 'vtype_vid.dict', vtype_vid)

    dict1 = load_dict(args.output, 'session_sid.dict')
    dict2 = load_dict(args.output, 'query_qid.dict')
    dict3 = load_dict(args.output, 'url_uid.dict')
    dict4 = load_dict(args.output, 'vtype_vid.dict')

    assert len(session_sid) == len(dict1)
    assert len(query_qid) == len(dict2)
    assert len(url_uid) == len(dict3)
    assert len(vtype_vid) == len(dict4)

    for key in dict1:
        assert dict1[key] == session_sid[key]
    for key in dict2:
        assert dict2[key] == query_qid[key]
    for key in dict3:
        assert dict3[key] == url_uid[key]
    for key in dict4:
        assert dict4[key] == vtype_vid[key]

    print('  - {}'.format('Done'))


def generate_train_valid_test(args):
    # load entity dictionaries
    print('  - {}'.format('loading entity dictionaries...'))
    session_sid = load_dict(args.output, 'session_sid.dict')
    query_qid = load_dict(args.output, 'query_qid.dict')
    url_uid = load_dict(args.output, 'url_uid.dict')
    vtype_vid = load_dict(args.output, 'vtype_vid.dict')

    # load infos_per_session.list
    print('  - {}'.format('loading the infos_per_session...'))
    infos_per_session = load_list(args.output, 'infos_per_session.list')

    # Separate all sessions into train : valid : test by config ratio
    session_num = len(infos_per_session)
    # train_session_num = int(session_num * args.trainset_ratio)
    # valid_session_num = int(session_num * args.validset_ratio)
    train_session_num = int(session_num * 0.6)
    valid_session_num = int(session_num * 0.2)
    test_session_num = session_num - train_session_num - valid_session_num
    train_valid_split = train_session_num
    valid_test_split = train_session_num + valid_session_num
    print('    - {}'.format('train/valid split at: {}'.format(train_valid_split)))
    print('    - {}'.format('valid/test split at: {}'.format(valid_test_split)))
    print('    - {}'.format('train sessions: {}'.format(train_session_num)))
    print('    - {}'.format('valid sessions: {}'.format(valid_session_num)))
    print('    - {}'.format('test sessions: {}'.format(test_session_num)))
    print('    - {}'.format('total sessions: {}'.format(session_num)))

    # split train & valid & test sessions
    print('  - {}'.format('generating train & valid & test data per session...'))
    random.seed(2333)
    random.shuffle(infos_per_session)
    train_sessions = infos_per_session[:train_valid_split]
    valid_sessions = infos_per_session[train_valid_split:valid_test_split]
    test_sessions = infos_per_session[valid_test_split:]
    assert train_session_num == len(train_sessions), 'train_session_num: {}, len(train_sessions): {}'.format(
        train_session_num, len(train_sessions))
    assert valid_session_num == len(valid_sessions), 'valid_session_num: {}, len(valid_sessions): {}'.format(
        valid_session_num, len(valid_sessions))
    assert test_session_num == len(test_sessions), 'test_session_num: {}, len(test_sessions): {}'.format(
        test_session_num, len(test_sessions))
    assert session_num == len(train_sessions) + len(valid_sessions) + len(
        test_sessions), 'session_num: {}, len(train_sessions) + len(valid_sessions) + len(test_sessions): {}'.format(
        session_num, len(train_sessions) + len(valid_sessions) + len(test_sessions))

    # generate train & valid & test queries
    print('  - {}'.format('generating train & valid & test data per queries...'))
    train_queries = []
    valid_queries = []
    test_queries = []
    for info_per_session in train_sessions:
        interaction_infos = info_per_session['interactions']
        for interaction_info in interaction_infos:
            train_queries.append(interaction_info)
    for info_per_session in valid_sessions:
        interaction_infos = info_per_session['interactions']
        for interaction_info in interaction_infos:
            valid_queries.append(interaction_info)
    for info_per_session in test_sessions:
        interaction_infos = info_per_session['interactions']
        for interaction_info in interaction_infos:
            test_queries.append(interaction_info)
    print('    - {}'.format('train queries: {}'.format(len(train_queries))))
    print('    - {}'.format('valid queries: {}'.format(len(valid_queries))))
    print('    - {}'.format('test queries: {}'.format(len(test_queries))))
    print('    - {}'.format('total queries: {}'.format(len(train_queries) + len(valid_queries) + len(test_queries))))

    # Write train/valid/test query information back to txt files
    print('  - {}'.format('writing back to txt files...'))
    print('    - {}'.format('writing into {}/train_per_query.txt'.format(args.output)))
    train_query_set = generate_data_per_query(train_queries, np.arange(0, len(train_queries)), args.output, 'train_per_query')
    print('    - {}'.format('writing into {}/valid_per_query.txt'.format(args.output)))
    valid_query_set = generate_data_per_query(valid_queries, np.arange(0, len(valid_queries)), args.output, 'valid_per_query')
    print('    - {}'.format('writing into {}/test_per_query.txt'.format(args.output)))
    test_query_set = generate_data_per_query(test_queries, np.arange(0, len(test_queries)), args.output, 'test_per_query')


def main():
    parser = argparse.ArgumentParser('TREC2014')
    parser.add_argument('--dataset', default='TREC2014.xml',
                        help='dataset name')
    parser.add_argument('--input', default='../dataset/TREC2014/',
                        help='input path')
    parser.add_argument('--output', default='./data/TREC2014',
                        help='output path')
    parser.add_argument('--dict_list', action='store_true',
                        help='generate dicts and lists for info_per_session/info_per_query')
    parser.add_argument('--train_valid_test_data', action='store_true',
                        help='generate train/valid/test data txt')
    parser.add_argument('--trainset_ratio', default=0.8,
                        help='ratio of the train session/query according to the total number of sessions/queries')
    parser.add_argument('--validset_ratio', default=0.1,
                        help='ratio of the valid session/query according to the total number of sessions/queries')
    args = parser.parse_args()

    if args.dict_list:
        # generate info_per_session & info_per_query
        print('===> {}'.format('generating dicts and lists...'))
        generate_dict_list(args)
    if args.train_valid_test_data:
        # load lists saved by generate_dict_list() and generates train.txt & valid.txt & test.txt
        print('===> {}'.format('generating train & valid & test data txt...'))
        generate_train_valid_test(args)


if __name__ == '__main__':
    main()
