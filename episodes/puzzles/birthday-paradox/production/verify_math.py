#!/usr/bin/env python3
"""Independent exact enumeration and rational-product checks; no empirical birthday claim."""
from fractions import Fraction
from itertools import product
from pathlib import Path
from math import comb
import json

def collision(days, people):
    distinct=Fraction(1)
    for k in range(people):
        distinct *= Fraction(max(days-k,0),days)
    return 1-distinct

def main():
    cases=0
    for days in range(1,7):
        for people in range(0,min(days+2,6)):
            assignments=list(product(range(days), repeat=people))
            repeats=sum(len(set(a))<people for a in assignments)
            assert Fraction(repeats,len(assignments)) == collision(days,people)
            cases+=1
    p=[collision(365,n) for n in range(367)]
    assert all(a<=b for a,b in zip(p,p[1:]))
    threshold=next(i for i,v in enumerate(p) if v>Fraction(1,2))
    assert threshold==23 and p[22]<Fraction(1,2)<p[23]
    assert p[0]==0 and p[1]==0 and p[366]==1
    specific=1-Fraction(364,365)**22
    report={'method':'Exact Fraction multiplication; independent exhaustive birthday assignments for small calendars','smallCalendarEnumerationCases':cases,'populationDomain':[0,366],'monotone':True,'firstOverHalf':threshold,'probability22':float(p[22]),'probability23':float(p[23]),'distinct23':float(1-p[23]),'pairsAmong23':comb(23,2),'specificPersonAmong23Other22':float(specific),'display':{'22':'47.57%','23':'50.73%','distinct23':'49.27%'},'boundaries':'365 uniform independent dates; leap day ignored; month/day only. A theoretical probability is not an empirical statistic or guarantee.'}
    Path(__file__).with_name('math-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
