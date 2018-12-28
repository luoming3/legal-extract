# coding:utf-8

import os
import re
import time
import codecs

import pandas as pd
from flashtext import KeywordProcessor


def ch2dig(date_str):
    date_map = {
        u'〇': '0', u'一': '1', u'二': '2', u'三': '3', u'四': '4',
        u'五': '5', u'六': '6', u'七': '7', u'八': '8', u'九': '9',
        u'十': '10'
    }
    if len(date_str) == 4:
        return (date_map[date_str[0]] + date_map[date_str[1]]
                + date_map[date_str[2]] + date_map[date_str[3]])
    elif len(date_str) == 1:
        return date_map[date_str]
    elif date_str[-1] == u'十' and len(date_str) == 2:
        return date_map[date_str[0]] + '0'
    elif date_str[0] == u'十' and len(date_str) == 2:
        return '1' + date_map[date_str[1]]
    elif len(date_str) == 3:
        return date_map[date_str[0]] + date_map[date_str[2]]


def get_content(path, kp):
    global count, l_id, l_id_list, l_num_list, relation_cid_list, relation_lid_list, filename
    global df_comp, l_court_name, l_court_type, l_date, l_dispute, l_content, l_accuser, l_accused
    file_name_list = os.listdir(path)

    for each_file in file_name_list:
        new_file = os.path.join(path, each_file)
        if os.path.isdir(new_file):
            get_content(new_file, kp)
        else:
            if os.path.splitext(each_file)[1] == '.txt':
                with codecs.open(new_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 一个法律裁决书里所有公司列表
                    each_relation_list = list(set(kp.extract_keywords(content)))
                # 如果能匹配出公司则提取legal信息
                if each_relation_list:
                    # 裁决书头部======================================================================================
                    pattern_head = ur'([\u4e00-\u9fa5]*?人民法院)\s*(.*)\s*[(（](.*?)[）)](.*?号)'
                    heads = re.search(pattern_head, content)
                    if heads:
                        court_name = heads.group(1)  # 法院名
                        court_type = ''.join(heads.group(2).split(' '))  # 裁决书类型
                        # court_year = heads.group(3)  # 裁决年份
                        court_num = heads.group(4)  # 裁决编号

                        filename.append(os.path.split(each_file)[1])
                        l_id_list.append(l_id)
                        l_num_list.append(court_num)
                        l_court_name.append(court_name)
                        l_court_type.append(court_type)

                        [relation_cid_list.append(list(df_comp[df_comp[u'公司名称'] == each_comp][u'企业ID'].values)[0])
                         for each_comp in each_relation_list]
                        relation_lid_list.extend([l_id] * len(each_relation_list))

                        l_id += 1

                        # 原告被告======================================================================================
                        next_search = True
                        accuser_list = [ur'上诉人（[、\u4e00-\u9fa5]*）', ur'原告（[、\u4e00-\u9fa5]*）',
                                        ur'申诉人（[、\u4e00-\u9fa5]*）', ur'再审申请人（[、\u4e00-\u9fa5]*）',
                                        u'申请执行人', u'申请人', u'公诉机关', u'上诉人', u'申诉人', u'原告']
                        accused_list = [ur'被上诉人（[、\u4e00-\u9fa5]*）', ur'被告（[、\u4e00-\u9fa5]*）',
                                        ur'被申诉人（[、\u4e00-\u9fa5]*）', ur'被申请人（[、\u4e00-\u9fa5]*）',
                                        u'被执行人', u'被告人', u'被申请人', u'被上诉人', u'被申诉人', u'被告', u'罪犯']
                        accuser_str = u'|'.join(accuser_list)
                        accused_str = u'|'.join(accused_list)
                        accuser_name_list = []
                        accused_name_list = []

                        # 主方：
                        accuser_pattern = ur'\n(' + accuser_str + ur')[：:]' + \
                                          ur'([\u4e00-\u9fa5][（）\u4e00-\u9fa5]*?)(（[：:\u4e00-\u9fa5]*?）)?[,，。\n]'
                        accuser_name = re.findall(accuser_pattern, content)
                        if accuser_name:
                            for name in accuser_name:
                                accuser_name_list.append(name[1])
                                # name[0] -> 原告, name[1] -> 原告名
                            next_search = False

                        # 被方：
                        accused_pattern = ur'\n(' + accused_str + ur')[：:]' + \
                                          ur'([\u4e00-\u9fa5][（）\u4e00-\u9fa5]*?)(（[：:\u4e00-\u9fa5]*?）)?[,，。\n]'
                        accused_name = re.findall(accused_pattern, content)
                        if accused_name:
                            for name in accused_name:
                                accused_name_list.append(name[1])
                                # name[0] -> 被告, name[1] -> 被告名
                            next_search = False

                        # 后面以，。\n结尾
                        if next_search:
                            accuser_pattern2 = ur'^(' + accuser_str + ur')' + \
                                               ur'([\u4e00-\u9fa5][（）\u4e00-\u9fa5]*?)(（[，,\u4e00-\u9fa5]*?）)?[,，。\n]'
                            accused_pattern2 = ur'^(' + accused_str + ur')' + \
                                               ur'([\u4e00-\u9fa5][（）\u4e00-\u9fa5]*?)(（[，,\u4e00-\u9fa5]*?）)?[,，。\n]'
                            stop_pattern = u'本院|如下[:：]'
                            with codecs.open(new_file, 'r', encoding='utf-8') as f:
                                accused_activation = False
                                for line in f.readlines():
                                    accuser_name2 = re.findall(accuser_pattern2, line)
                                    if accuser_name2 and not accused_activation:
                                        for name in accuser_name2:
                                            accuser_name_list.append(name[1])
                                    # 当匹配了被告 又出现原告时应判结束
                                    elif accuser_name2 and accused_activation:
                                        break
                                    # 搜索到 “本院” 二字应结束
                                    elif re.search(stop_pattern, line):
                                        break
                                    else:
                                        accused_name2 = re.findall(accused_pattern2, line)
                                        if accused_name2:
                                            for name in accused_name2:
                                                accused_name_list.append(name[1])
                                            accused_activation = True
                        if accuser_name_list:
                            l_accuser.append(', '.join(accuser_name_list))
                        else:
                            l_accuser.append('')
                        if accused_name_list:
                            l_accused.append(', '.join(accused_name_list))
                        else:
                            l_accused.append('')

                        # 判决日期======================================================================================
                        date_pattern = ur'(审|陪|执).*\n([〇\u4e00-\u9fa5]*)\n(书|执)'
                        date_result = re.findall(date_pattern, content)
                        if date_result:
                            try:
                                date_list = re.sub(ur'([年月日])', ' ', date_result[0][1]).strip().split(' ')
                                year_str = date_list[0]
                                mon_str = date_list[1]
                                day_str = date_list[2]
                                year_num = ch2dig(year_str)
                                mon_num = ch2dig(mon_str)
                                day_num = ch2dig(day_str)
                                legal_date = year_num + '年' + mon_num + '月' + day_num + '日'
                                l_date.append(legal_date)
                            except Exception as error:
                                print error
                                l_date.append('')
                        else:
                            l_date.append('')

                        # 裁定内容======================================================================================
                        judge_pattern = ur'(裁定|通知|判决)如下：\n((.*\n)*?)(本裁定|如不服|申请人|如果)'

                        # 结尾可能是审判长
                        judge_content = re.findall(judge_pattern, content)
                        if judge_content:
                            # judge_content[0][1]   # 执行内容
                            l_content.append(judge_content[0][1])
                        else:
                            l_content.append('')

                        # 纠纷类型======================================================================================
                        # 被告.*一案
                        if accused_name_list:
                            name_pre = u'(' + u"|".join(accused_name_list) + u')'
                            pattern_dispute = name_pre + u'(（[\u4e00-\u9fa5]*）)?' + ur'([\u4e00-\u9fa5]*)' + ur'一案'
                            dispute_type = re.findall(pattern_dispute, content)
                            if dispute_type:
                                type_result = dispute_type[0][-1]
                                l_dispute.append(type_result)
                            else:
                                l_dispute.append('')
                        else:
                            l_dispute.append('')


if __name__ == '__main__':
    count = 0
    l_id = 10000001
    l_id_list = []
    l_num_list = []
    l_court_name = []
    l_court_type = []
    l_date = []
    l_dispute = []
    l_content = []
    l_accuser = []
    l_accused = []
    relation_cid_list = []
    relation_lid_list = []
    filename = []
    file_path = '/home/luoming/newproject/hubei_legal/null/'
    t0 = time.clock()
    df_comp = pd.read_csv('comp_id_name.csv', encoding='utf-8')
    comp_name_list = list(df_comp[u'公司名称'].values)

    key_processor = KeywordProcessor()
    # 将公司名作为关键词加入到 KeywordProcessor 中
    key_processor.add_keywords_from_list(comp_name_list)

    get_content(file_path, key_processor)
    print time.clock() - t0

    # 建立公司表
    # c_id = 100001
    # c_id_list = []
    # company_list = []
    # with codecs.open('company_name.txt', 'r', encoding='utf-8') as f:
    #     for line in f.readlines():
    #         company_list.append(line.strip())
    #         c_id_list.append(c_id)
    #         c_id +=1
    # df_comp = pd.DataFrame({'c_id': c_id_list, 'c_name': company_list})
    # df_comp.to_csv('com_id_name.csv', index=False, encoding='utf-8')

    # 建立法律表
    # df_legal = pd.DataFrame({'l_id': l_id_list, 'l_num': l_num_list, 'l_court_name': l_court_name,
    #                          'l_court_type': l_court_type, 'l_date': l_date, 'l_dispute': l_dispute,
    #                          'l_content': l_content, 'l_accuser': l_accuser, 'l_accused': l_accused},
    #                         columns=['l_id', 'l_num', 'l_court_name', 'l_court_type', 'l_date',
    #                                  'l_dispute', 'l_accuser', 'l_accused', 'l_content'])
    # df_legal.to_csv('legal_id_num.csv', index=False, encoding='utf-8')

    # 建立关系表
    # df_relation = pd.DataFrame({'c_id': relation_cid_list, 'l_id': relation_lid_list})
    # df_relation.to_csv('relation_id.csv', index=False, encoding='utf-8')
