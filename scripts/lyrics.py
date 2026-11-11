"""Lyric / sample spec
Notation inside the syllable text:
  space  -> next word, next note        '-' -> same word, next note
  '&'    -> next word, SAME note        '+' -> same word, SAME note (note is split in two)
  '~'    -> tie (hold previous syllable over one more note)    '_' -> leave a note unsung
 for 楚门的圆形监狱.
Each sung chunk: (id, speaker, src_start, src_end, 'syl-la-bles', octave_shift)
Syllables are separated by '-' inside words and ' ' between words.
'~' = tie: extend previous syllable over the next melody note.
Phrases list the chunk ids in melody order.
"""
SUNG = [
 # ---- A1 : Christof's doctrine
 ('c01','christof',3970.74,3973.62,"_ We ac-cept the re-al-i-ty of the world with which we're pre-sent-ed"),
 ('c02','christof',3973.90,3975.12,"It's&as sim-ple as that"),
 ('c03','marlon',  119.30, 120.08,"It's all real"),
 ('c04','christof',  36.90,  39.62,"No scripts no cue cards"),
 ('c05','christof',  42.10,  42.72,"it's gen-u-ine"),
 ('c06','christof',4808.86,4809.84,"Cue the sun"),
 # ---- A2 : daily routine
 ('c07','truman',  167.72, 168.52,"Good mor-ning"),
 ('c08','radio',  1769.63,1771.12,"oth-er ~ beau-ti+ful day ~ in par-a-dise"),
 ('c10','truman',  168.92, 171.26,"Oh and&in case I don't see you good af-ter-noon"),
 ('c11','truman',  171.40, 172.40,"good eve-ning and good night"),
 # ---- B1 : Sylvia's warning
 ('c12','sylvia', 1587.08,1587.68,"Tru-man"),
 ('c13','sylvia', 1588.50,1589.36,"Lis-ten to me"),
 ('c14','sylvia', 1590.70,1592.24,"Ev-ery-bod-y knows ev-ery-thing you do"),
 ('c15','sylvia', 1592.38,1593.66,"They're pre+tend-ing Tru-man ~"),
 ('c16','sylvia', 1618.10,1620.52,"It's a&set it's a show ~ Ev+ery-bod-y's watch-~-ing you"),
 # ---- B2 : the watcher / the answer
 ('c17','truman', 5542.70,5543.86,"Who are you"),
 ('c18','christof',5615.82,5618.18,"I have been watch-ing you your whole life ~"),
 ('c19','christof',5621.06,5623.06,"I&was watch-ing when&you were born ~"),
 ('c20','christof',5625.68,5628.48,"I was watch-ing when you took your first ~ step"),
 ('c21','truman', 5597.38,5599.00,"You nev-er had&a cam-era in my head ~ ~"),
 ('c22','truman', 5598.36,5599.00,"in my head ~"),
]
# melody phrases: (name, [chunk ids], octave shift for lead in semitones)
PHRASES = [
 ('A1', ['c01','c02','c03','c04','c05','c06'], -12),
 ('A2', ['c07','c08','c10','c11'], -12),
 ('B1', ['c12','c13','c14','c15','c16'], -12),
 ('B2', ['c17','c18','c19','c20','c21','c22'], -12),
]
# spoken (un-pitched) lines: (id, speaker, src_start, src_end, text)
SPOKEN = [
 ('s01','host',   3696.50,3701.05,"An entire human life, recorded on an intricate network of hidden cameras"),
 ('s02','host',   3700.95,3708.35,"and broadcast live and unedited, 24 hours a day, seven days a week, to an audience around the globe"),
 ('s03','christof',5644.84,5646.70,"You can't leave, Truman."),
 ('s04','christof',5650.12,5651.16,"You belong here."),
 ('s05','christof',5654.60,5655.64,"With me."),
 ('s06','christof',5658.26,5659.40,"Talk to me."),
 ('s07','christof',5660.94,5662.10,"Say something."),
 ('s08','christof',5667.08,5668.84,"Say something, goddammit!"),
 ('s09','christof',5668.84,5669.94,"You're on television!"),
 ('s10','christof',5670.38,5672.20,"You're live to the whole world!"),
 ('s11','truman', 5689.84,5691.28,"In case I don't see ya"),
 ('s12','truman', 5692.68,5694.92,"Good afternoon, good evening, and good night."),
 ('s13','crowd',  5699.00,5712.00,"(cheering)"),
 ('s14','christof-staff',5747.04,5748.08,"Cease transmission."),
 ('s15','guard',  5757.32,5758.20,"What else is on?"),
 ('s16','sylvia', 4056.96,4058.62,"He's not a performer. He's a prisoner."),
 ('s17','christof',5556.30,5557.66,"You're the star."),
 ('s18','radio',  1775.70,1779.60,"Good, good, good, good, good, good"),
 ('s19','truman', 2816.90,2819.30,"Ha ha! Ha!"),
 ('s20','christof',4808.86,4809.84,"Cue the sun"),
]


def parse(text):
    """-> list of items: ('skip',) | ('tie',) | ('syl', text, new_word, same_note)"""
    items = []
    for grp in text.split():
        if grp == '_': items.append(('skip',)); continue
        if grp == '~': items.append(('tie',)); continue
        first_in_grp = True
        for wi, word in enumerate(grp.split('&')):
            cur = ''; sep = None; parts = []
            for ch in word:
                if ch in '-+':
                    parts.append((cur, sep)); cur = ''; sep = ch
                else: cur += ch
            parts.append((cur, sep))
            for pi, (txt, sp) in enumerate(parts):
                if txt == '~': items.append(('tie',)); continue
                new_word = (pi == 0)
                same = (wi > 0 and pi == 0) or (sp == '+')
                items.append(('syl', txt, new_word, same))
    return items
