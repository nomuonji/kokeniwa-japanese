#!/usr/bin/env python3
"""Rebuild the interpretation corpus from the reviewed grammar corpus.

The source grammar quiz is read-only.  Its answer is inserted into each blank
so this book contains complete Japanese sentences, not cloze exercises.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUIZ = ROOT / "data" / "quiz_problems.jsonl"
OUT = ROOT / "data" / "reading_problems.jsonl"
LEVEL = {"n5": 1, "n4": 1, "n3": 2, "n2": 2, "n1": 3}
COMPLETED_SENTENCES = {
    47: "安ければ、買います。",
    58: "休みの日は映画とか音楽とかを楽しみます。",
    78: "今、家を出るところです。", 92: "疲れていたので、電気をつけたまま寝てしまいました。",
    96: "机の上に読みかけの本が置いてある。", 98: "「袋、ご利用ですか」「あ、大丈夫です」",
    107: "彼は英語どころか、フランス語もドイツ語も話せる。",
    125: "そんな運転をしていたら、事故を起こしかねないよ。",
    145: "泣きたいほど悔しかった。",
}
ROW_OVERRIDES = {
    83: {
        "sentence_ja": "取引先からの依頼に対し、「承知いたしました。明日までに対応いたします」と答えた。",
        "translation_en": "In response to the client's request, I said, 'Understood. We will take care of it by tomorrow.'",
        "explanation_en": "承知いたしました is a humble, client-appropriate way to acknowledge a request. 対応いたします uses the humble form いたす for the speaker's or their company's action.",
    },
    104: {
        "sentence_ja": "レストランで店員に「何名様ですか」と聞かれた。",
        "translation_en": "At the restaurant, a server asked, 'How many people are in your party?'",
        "explanation_en": "何名様 is the customer-service form of 何人. 名 is a formal counter for people, and 様 adds respect toward the guests.",
    },
    109: {
        "sentence_ja": "部下が上司に「お疲れ様です」と声をかけた。",
        "translation_en": "A subordinate greeted their manager by saying, 'Thank you for your hard work.'",
        "explanation_en": "お疲れ様です is a conventional workplace greeting usable toward a superior. ご苦労様 is traditionally used downward, from a superior to a subordinate.",
    },
    119: {
        "sentence_ja": "店員は「ご注文がお決まりになりましたら、お呼びください」と案内した。",
        "translation_en": "The server said, 'Please call me when you have decided on your order.'",
        "explanation_en": "お決まりになる is honorific language for the customer's action. お呼びください is the respectful request pattern お + verb stem + ください.",
    },
    128: {
        "sentence_ja": "お客様が資料をご覧になりました。",
        "translation_en": "The customer looked over the materials.",
        "explanation_en": "ご覧になる is the honorific form of 見る and appropriately elevates the customer's action. The humble 拝見する would instead describe the speaker's own act of looking.",
    },
    130: {
        "sentence_ja": "今日は暑いですね。",
        "translation_en": "It's hot today, isn't it?",
        "explanation_en": "Sentence-final ね invites agreement about information both speakers can perceive. It softens the statement into a shared observation.",
    },
}
INTERPRETATION_NOTES = {
    16: "しか pairs with a negative predicate: 百円しかありません means 'there is no more than one hundred yen' and presents that amount as limited.",
    19: "〜わけではない partially denies an assumption: the speaker denies disliking Japanese food, while 毎日は食べたくない adds the narrower limitation 'not every day'.",
    20: "「遅れがち」 means 'tend to be late' and carries an undesirable nuance; 「遅れ気味」 is also possible Japanese, but this sentence uses がち.",
    46: "「つもりです」 presents the speaker's own intention. 「予定です」 can also be natural in a different context, but it would frame the move as a scheduled arrangement.",
    56: "「言いづらい」 focuses on the speaker's emotional difficulty in saying this to the person. 「言いにくい」 is also possible but is more neutral.",
    57: "「公園を走る」 presents the park as the route traversed. 「公園で走る」 is also grammatical, but it focuses on the location of the action.",
    74: "「使わずに」 is the written/formal 'without using'. 「使わないで」 is also common in speech; the full sentence here deliberately uses ずに.",
    77: "「行かないで」 is an everyday warning. 「行くな」 is grammatical but much harsher, so the chosen wording affects tone rather than bare truth conditions.",
    85: "「水をやる」 is a traditional expression for watering plants. 「水をあげる」 is also widely used in contemporary Japanese.",
    137: "「伺ってもよろしいでしょうか」 humbly frames a visit to the listener. 「参っても」 can also be grammatical, but is less specifically deferential toward the destination.",
    28: "得意 describes an area in which the speaker feels capable. 上手 can describe skill too, but using it about oneself may sound self-congratulatory in this context.",
    49: "〜ていただけませんか is a highly polite request that literally asks whether the listener could do the action for the speaker. It is softer than 〜てください.",
    71: "〜ざるを得ない means being forced by circumstances to do something. Here the typhoon left the organizers no practical choice but to cancel the event.",
    89: "〜つつある expresses a gradual change in progress. 減りつつある modifies 町 and says that the populations of those towns are currently declining.",
    143: "〜に違いない expresses a strong inference. The lights being on are the evidence for concluding that he must already be home.",
}

# These are locally plausible misreadings for the thirteen comprehension
# checks retained from the supplementary set.  The remaining problems are
# open English-rendering tasks.
OPTIONS = {
152: ["Anyone may join the training, whether or not they have experience.", "Only applicants with some prior experience may join the training.", "Experience is not required, but attendance is mandatory for everyone.", "The training is open only to people who can document their experience."],
156: ["The law was enacted for the purpose of protecting personal information.", "The law makes individuals solely responsible for protecting their data.", "The law was enacted to promote the wider use of personal information.", "The law protects personal information only after it has been disclosed."],
160: ["Disaster preparedness should be kept in mind precisely in everyday life.", "Preparedness should be considered mainly when a disaster is already happening.", "Only emergency professionals need to prepare during ordinary life.", "Everyday routines should take priority over preparing for disasters."],
164: ["Failing to keep even basic promises makes it difficult to earn trust.", "Once trust has been earned, keeping minor promises is no longer important.", "Explaining why a promise was broken is enough to preserve trust.", "Trust remains difficult to earn even when basic promises are kept."],
168: ["We cannot say with certainty that the method is the best.", "The method is probably the best, although some details remain uncertain.", "The speaker is certain that the method is not the best.", "The speaker is unwilling to compare this method with any other."],
172: ["We organized operational issues that experts had identified as easy to overlook.", "We concluded that experts had overlooked every problem in the system's operation.", "Experts reorganized the system after its operational problems were resolved.", "We organized problems that experts said had already been corrected."],
176: ["The proposed method has the advantage of keeping costs down.", "The proposed method makes future costs easier to predict.", "The method reduces costs only because the proposal was rejected.", "The sentence says cost is a concern, not an advantage of the method."],
180: ["What is needed is a system that does not rely on individual effort alone.", "What is needed is a system that rewards greater individual effort.", "The system should eliminate the need for any individual effort.", "No system can reduce dependence on individual effort."],
184: ["Focusing too much on results can make us lose sight of learning in the process.", "Results matter more because learning from the process is uncertain.", "Focusing too much on the process can make us lose sight of results.", "Learning from the process matters only when the final result is poor."],
188: ["Judging from his explanation, there appears to be good reason for the choice.", "His explanation proves that the choice was correct.", "His explanation suggests that the choice has no adequate basis.", "Regardless of his explanation, the choice appears unreasonable."],
192: ["It is best to be thoroughly prepared in advance.", "Advance preparation is advisable only when the risk is high.", "Preparation should be limited to the minimum that seems necessary.", "Too much advance preparation is likely to make matters worse."],
196: ["Appropriate measures cannot be developed without listening to those affected.", "Measures may be drafted before listening to those affected and revised afterward.", "It is enough to consult representatives rather than the people directly affected.", "Listening to those affected is helpful but not necessary for appropriate measures."],
200: ["A clue to a solution lies precisely in continued dialogue among people with different positions.", "Dialogue becomes useful only after the different sides narrow their differences.", "A solution requires everyone involved to adopt the same position.", "Repeated dialogue among different sides makes a solution harder to find."],
}

# Corrections from the publication-wide language and assessment review.  These
# are applied after importing both the original 150 grammar items and the
# 50-item supplement so a rebuild cannot reintroduce a corrected issue.
REVIEW_CORRECTIONS = {
    1: {"point": "を (direct object)", "explanation_en": "見ました (saw) is transitive here, and 猫 is the thing being seen. The direct object is therefore marked by を: 猫を見ました."},
    9: {"sentence_ja": "先生は明日、こちらの学校にいらっしゃるそうです。", "translation_en": "I hear the teacher will be coming to our school tomorrow.", "explanation_en": "いらっしゃる is the honorific (sonkeigo) form of 来る here. こちらの学校 and the context establish the direction as coming to the speaker's school."},
    17: {"explanation_en": "To say 'not as cold as last year,' use the comparison standard + ほど + negative: 去年ほど寒くない. より can also occur with a negative predicate, but it produces a different comparison rather than this 'not as ... as' pattern."},
    27: {"sentence_ja": "病院の中では大きな声で話してはいけません。"},
    30: {"translation_en": "If you're looking for sushi, the restaurant in front of the station is good.", "explanation_en": "なら takes up sushi as the topic and gives advice about it: 寿司なら means 'if we're talking about sushi.' A form such as 寿司だったら is also grammatical, but なら is the direct topic-taking conditional used here."},
    35: {"explanation_en": "より marks the standard of comparison: 飛行機より安い means 'cheaper than the plane.' ほど appears in other comparison patterns, including 飛行機ほど高くない ('not as expensive as the plane'), but that is a different sentence structure."},
    39: {"point": "に (destination and purpose)", "explanation_en": "The first に marks the destination, 家に, and the second marks the purpose of movement, 遊びに. The destination could also take へ, but the purpose before 来る takes に."},
    65: {"translation_en": "We will call you later."},
    72: {"translation_en": "\"Thank you very much.\" \"Thank you, too.\""},
    75: {"explanation_en": "Inside a relative clause, the subject is normally marked by が (or sometimes の): 母が作ったカレー. A topic-marking は is generally avoided in this neutral pattern, though contrastive は can occur in more specialized contexts."},
    80: {"point": "なるほど (acknowledging an explanation)", "sentence_ja": "「この道をまっすぐ行くと駅に着きますよ」「なるほど、分かりました」", "translation_en": "\"Go straight down this road and you'll reach the station.\" \"I see. Got it.\"", "explanation_en": "なるほど signals that an explanation now makes sense to the listener: 'I see.' It is a natural response after receiving and understanding new information."},
    89: {"translation_en": "In rural Japan, a growing number of towns are experiencing population decline.", "explanation_en": "〜つつある expresses a gradual change in progress. The clause 人口が減りつつある modifies 町, describing towns whose populations are currently declining."},
    91: {"explanation_en": "When reporting another person's desire from observable behavior, Japanese commonly uses 〜たがる: 飼いたがっています. Plain 〜たい can still appear in quotations and contexts where the person's stated intention is being reported directly."},
    92: {"translation_en": "I was tired, so I fell asleep with the light still on."},
    101: {"translation_en": "Please refrain from making phone calls while on board."},
    113: {"sentence_ja": "去年、日本語を習いはじめました。"},
    119: {"point": "お〜になる／お〜ください", "translation_en": "The server said, 'Please call a member of staff once you've decided what to order.'"},
    122: {"translation_en": "I ate two bowls of ramen!", "explanation_en": "Bowls and cups of food or drink take 〜杯: ラーメン二杯. The particle も presents two bowls as a surprisingly large amount, which the exclamation in the English rendering conveys."},
    128: {"point": "Honorific ご覧になる"},
    141: {"translation_en": "Calling his room dirty is an understatement—it's more like a storage room."},
    154: {"sentence_ja": "大雪のため、航空会社は多くの便の欠航を余儀なくされた。", "translation_en": "Because of heavy snow, the airline was forced to cancel many flights.", "explanation_en": "「欠航を余儀なくされた」 means that circumstances forced the airline to cancel flights. The airline is the party compelled to act; 多くの便の欠航 is the action it had no choice but to take."},
    159: {"translation_en": "Interaction with other countries gradually changed the atmosphere of the town."},
    170: {"translation_en": "While continuing her research, she also mentors younger students."},
    172: {"sentence_ja": "私たちは、専門家が指摘した制度運用上の見落とされがちな問題を整理した。", "translation_en": "We organized operational issues that experts had identified as easy to overlook.", "explanation_en": "「専門家が指摘した」 modifies 「制度運用上の見落とされがちな問題」. The main predicate is 「整理した」, whose explicit subject is 「私たち」."},
    173: {"translation_en": "Support from groups with a long history in the area is helping sustain disaster victims' daily lives.", "explanation_en": "「地域で長く活動してきた団体による支援」 is support provided by groups with a long history in the area. 「被災者の生活を支えている」 says that support is sustaining victims' daily lives."},
    177: {"translation_en": "According to the report, half of the survey participants feel anxious."},
    188: {"translation_en": "Judging from his explanation, there appears to be good reason for that choice."},
    191: {"translation_en": "As of today, this counter will no longer be accepting requests.", "explanation_en": "「本日をもって」 is a formal cutoff expression meaning 'as of today.' 「受付」 means that the counter will stop accepting the relevant requests or submissions; the exact type depends on the surrounding context."},
}
SUPPLEMENT_EXPLANATIONS = {
151:"「建設をめぐって」 means 'over/concerning the construction'; 「意見が分かれている」 says residents hold differing views, not that construction is complete.",
152:"「経験の有無にかかわらず」 includes both people with experience and people without it; the sentence explicitly removes experience as a condition for participation.",
153:"「年齢を問わず」 is a formal 'regardless of age'. 「だれでも」 confirms that no age group is excluded from the course.",
154:"「欠航を余儀なくされた」 is a formal passive: circumstances forced the flights to be canceled. It does not imply a voluntary decision by the airlines.",
155:"「世代を超えた協力」 means cooperation across generations, and 「求められている」 reports that such cooperation is needed rather than already achieved.",
156:"「個人情報の保護を目的として」 states the law's purpose: protecting personal information. 「制定された」 is the passive form 'was enacted'.",
157:"「利用者の声を通じて」 means through users' feedback. 「見えてきた」 describes issues gradually becoming clear, not users themselves becoming visible.",
158:"「地域ならではの」 means unique to that region, while 「生かした」 says the dishes make use of those ingredients; it does not claim all regional food is identical.",
159:"「交流を契機に」 identifies international exchange as the catalyst. 「少しずつ変わった」 presents a gradual change in the town's atmosphere.",
160:"「日常生活の中でこそ」 uses こそ for emphasis: disaster preparedness should be consciously considered precisely in ordinary daily life.",
161:"「信頼に足る」 means worthy of trust. The following 「が」 limits the praise: the evidence still needs to be checked.",
162:"「反対するにしても」 means even if one opposes the proposal. The sentence keeps the requirement to listen to the other side.",
163:"Potential 「できる」 plus 「ものなら」 expresses a wish the speaker sees as difficult or unrealistic: they would advise their younger self if it were possible.",
164:"「守れないようでは」 gives a critical condition: if someone cannot keep even basic promises, earning trust will be difficult.",
165:"「驚きを禁じ得ない」 is a formal expression for being unable to suppress surprise after hearing the news.",
166:"Age plus 「にして」 emphasizes the notable point at which something happened; he founded the company for the first time at fifty.",
167:"「言わざるを得ない」 means one has no choice but to say so. The writer reluctantly concludes that insufficient preparation caused the failure.",
168:"「言い切れない」 means cannot state something categorically. The sentence withholds the absolute claim that the method is best.",
169:"「長年の経験があってこそ」 means only because of many years of experience; that experience is presented as a necessary basis for the work.",
170:"「研究を続けるかたわら」 means alongside continuing research. Teaching younger students is an additional ongoing role.",
171:"The clause 「委員会が昨年から検討してきた」 modifies 「案」. 「ようやく」 signals that its announcement next month comes after a long wait.",
172:"「制度の運用上」 means in the operation of the system, and 「見落とされがちな」 modifies problems that tend to be overlooked.",
173:"「長く活動してきた団体による支援」 is support provided by groups active in the region for a long time; 「支えている」 states that it sustains victims' lives now.",
174:"「考えるべきなのは」 sets the focus. The not A but B pattern contrasts what to change with the more fundamental question of why to change it.",
175:"「応募があったことから」 gives the reason for the decision. The unexpectedly high number of applications led to changing the venue.",
176:"The quoted clause 「費用を抑えられる」 states the advantage of the proposed method: costs can be kept down.",
177:"「報告書によれば」 marks the report as the source. 「半数が不安を感じている」 says half, not all, of the survey participants feel anxious.",
178:"「私が驚いたのは」 makes the following nominalized clause the focus: he spoke about his failure without hiding it.",
179:"「予算が限られている以上」 means given that the budget is limited. It supplies the basis for saying every request cannot be met.",
180:"「個人の努力だけに頼らない」 modifies 「仕組み」. The needed solution is a system, not merely more effort by individuals.",
181:"「課題があるものの」 concedes that the plan has issues, but 「中止するほどではない」 says they are not serious enough to cancel it now.",
182:"「批判というより」 corrects the first description: the remarks are better understood as anxiety about the situation than as criticism.",
183:"「情報が十分でない以上」 establishes a condition, and 「わけにはいかない」 means social or practical circumstances make an immediate conclusion unacceptable.",
184:"「重視するあまり」 means to such an excessive degree that a bad result follows. Overvaluing results can make one lose sight of learning in the process.",
185:"「便利である反面」 presents the reverse side of convenience: the system also asks users to bear a certain burden.",
186:"「時間がかかって当然だ」 says it is natural or to be expected that regaining trust once lost takes time.",
187:"「助言を受けたからといって」 means 'just because advice was received'. 「必ず成功するわけではない」 rejects any guarantee of success.",
188:"「説明を聞く限り」 limits the judgment to what the speaker has heard. 「十分な理由があるようだ」 is a cautious inference, not proof.",
189:"The paired pattern 「先送りにすればするほど」 means the more the problem is postponed, the more difficult its solution becomes.",
190:"「偶然ではなく」 rejects chance, while 「地道な改善を重ねた成果」 attributes the result to repeated steady improvements.",
191:"「本日をもって」 is a formal cutoff expression meaning as of today; applications at this counter will end on that date.",
192:"「〜に越したことはない」 means there is nothing better than doing something. It recommends thorough preparation in advance.",
193:"「新たな証拠が出ない限り」 means unless new evidence emerges. The speaker does not intend to change the judgment under that condition.",
194:"「一つの分野だけでは」 limits the means available. 「解決し得ない」 formally says the problem cannot be solved by one field alone.",
195:"「社会の変化に伴い」 means along with social change. 「見直されつつある」 describes the way people work as gradually being reconsidered.",
196:"「当事者の声を聞かずして」 is a formal 'without listening to those concerned'. It presents that listening as necessary before forming appropriate measures.",
197:"「評価に値する」 means deserves recognition, but 「残っていないわけではない」 is a partial negative: some issues still remain.",
198:"「変えること自体」 refers to changing the system itself. 「目的化してはならない」 warns that this action must not turn into an end in itself.",
199:"「正しかったかどうか」 is an embedded whether-clause. 「待たなければ分からない」 says future results are needed before the judgment can be known.",
200:"「対話を重ねることにこそ」 uses こそ to emphasize that repeated dialogue among people in different positions is where a clue to a solution lies.",
}
TRANSLATION_OVERRIDES = {
    101: "Please refrain from talking on the phone while on the train.",
    102: "I got caught in the rain on my way home, and my clothes were soaked.",
    122: "I ate two whole bowls of ramen.",
    183: "Given that we do not have enough information, we cannot reach a conclusion right away.",
    188: "Judging from his explanation, there seems to be good reason for that choice.",
}


def main():
    old_supplement = [json.loads(x) for x in OUT.read_text(encoding="utf-8").splitlines() if x.strip()][150:]
    if len(old_supplement) != 50:
        raise SystemExit("Expected the reviewed 50-row supplement already present in reading_problems.jsonl.")
    rows = []
    for source in (json.loads(x) for x in QUIZ.read_text(encoding="utf-8").splitlines() if x.strip()):
        answer = source["choices"][source["answer_index"]]
        override = ROW_OVERRIDES.get(source["id"], {})
        sentence = override.get("sentence_ja", COMPLETED_SENTENCES.get(
            source["id"], source["sentence_ja"].replace("___", answer)))
        if "___" in sentence:
            raise ValueError(f"unfilled blank in source item {source['id']}")
        rows.append({"id": len(rows)+1, "category": source["category"], "point": source["point"],
            "difficulty": LEVEL[source["level"]], "format": "translation",
            "sentence_ja": sentence, "question_en": "Translate this Japanese sentence into natural English.",
            "choices": [], "answer_index": None,
            "translation_en": override.get("translation_en", TRANSLATION_OVERRIDES.get(
                source["id"], source["translation_en"])),
            "explanation_en": override.get("explanation_en", INTERPRETATION_NOTES.get(
                source["id"], source["explanation_en"])),
            "status": "published", "used_at": ""})
    for source in old_supplement:
        item = dict(source); item["id"] = len(rows)+1; item["status"] = "published"; item["used_at"] = ""
        if item["id"] in OPTIONS:
            item["format"] = "quiz"; item["question_en"] = "Which interpretation best matches the Japanese sentence?"
            options = list(OPTIONS[item["id"]])
            correct = options.pop(0)
            answer = 0 if item["id"] == 152 else (item["id"] // 4) % 4
            options.insert(answer, correct)
            item["choices"] = options; item["answer_index"] = answer
        else:
            item["format"] = "translation"; item["question_en"] = "Translate this Japanese sentence into natural English."; item["choices"] = []; item["answer_index"] = None
        item["translation_en"] = TRANSLATION_OVERRIDES.get(item["id"], item["translation_en"])
        item["explanation_en"] = SUPPLEMENT_EXPLANATIONS[item["id"]]
        rows.append(item)
    for item in rows:
        item.update(REVIEW_CORRECTIONS.get(item["id"], {}))
    assert len(rows) == 200 and len({r['sentence_ja'] for r in rows}) == 200
    OUT.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows)+"\n", encoding="utf-8")
    print(f"Rebuilt {len(rows)} complete, unique sentences; {sum(r['format']=='quiz' for r in rows)} contextual quizzes.")

if __name__ == "__main__":
    main()
