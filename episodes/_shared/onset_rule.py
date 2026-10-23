# Nolan onset rule, adopted 2026-10-21 for EP.06 onward (shared by label_onset_strict.py; mirror in validate.py).
#  1. Find a pause: >= 2 frames continuously below -40 dB that ends after the previous char's ASR end.
#     Search back from the cue char's ASR start to max(start-15f, previous char's ASR start); if the ASR start
#     itself sits inside such a pause, that pause is used.
#  2. Onset = first moment after the pause at >= -45 dB that is a fricative, plosive or voiced sound.
#     Breath does not count: it is skipped and the onset is where real speech begins.
#  3. No qualifying pause (continuous speech) -> onset = cue char's ASR start (source 'asr').
#  All values are fractional frames (30 fps, 1/4-frame hop); compare cue frames against them without rounding.
import numpy as np
FPS=30
PAUSE_DB=-40.0     # pause level (10 ms RMS)
PAUSE_MIN=2.0      # pause length, frames
SOUND_DB=-45.0     # onset level (10 ms RMS)
HOP=0.25           # analysis hop, frames
WIN=0.01           # RMS / centroid window, s, centred
LOOKBACK=15.0      # frames before the ASR start searched for the pause (never before the previous char ASR start)
# breath exclusion (unvoiced stretch after the pause, before speech):
VOICED_R=0.45           # normalised autocorrelation peak, pitch 70-400 Hz, 30 ms window => voiced
BREATH_CENTROID=3000.0  # Hz; >= this = fricative/plosive noise (s sh x c z q j t k p bursts)
BREATH_MAX_DB=-30.0     # louder than this = consonant, never breath
BURST_JUMP=9.0          # dB rise within 1/4 frame = plosive burst
BREATH_MIN=0.18         # s; quiet low-centroid unvoiced run longer than this before speech = breath (skipped); shorter = h/f consonant
# a breath-like run that drops back below SOUND_DB before speech is a detached breath and is skipped.
class Rule:
  def __init__(s,x,sr):
    s.x=np.asarray(x,np.float64);s.sr=sr;s.spf=sr/FPS;s.w=int(WIN*sr)
  def _win(s,f,n):
    a=max(0,int(round(f*s.spf-n/2)));return s.x[a:a+n]
  def db(s,f):
    y=s._win(f,s.w);return 20*np.log10(np.sqrt(np.mean(y**2))+1e-9) if len(y) else -120.0
  def voiced(s,f):
    n=int(0.03*s.sr);y=s._win(f,n);y=y-y.mean()
    if len(y)<n or np.sum(y*y)<1e-10:return False
    lo,hi=int(s.sr/400),int(s.sr/70);c=np.correlate(y,y,'full')[len(y)-1:];c/=c[0]+1e-12
    return float(c[lo:min(hi,len(c)-1)].max())>=VOICED_R
  def centroid(s,f):
    y=s._win(f,s.w);S=np.abs(np.fft.rfft(y*np.hanning(len(y))))**2;fr=np.fft.rfftfreq(len(y),1/s.sr)
    return float((S*fr).sum()/(S.sum()+1e-18))
  def strong(s,f,prev_db):
    d=s.db(f)
    if s.voiced(f):return 'voiced'
    if s.centroid(f)>=BREATH_CENTROID:return 'fricative/plosive'
    if d>BREATH_MAX_DB or d-prev_db>=BURST_JUMP:return 'fricative/plosive'
    return None
  def first_sound(s,f,limit):
    skipped=[]
    while f<limit:
      while f<limit and s.db(f)<SOUND_DB:f+=HOP
      if f>=limit:break
      r0=f;prev=s.db(f-HOP);g=f
      while g<limit:
        d=s.db(g)
        if d<SOUND_DB:break
        k=s.strong(g,prev)
        if k:
          if (g-r0)/FPS<=BREATH_MIN:return r0,(k if g==r0 else 'fricative (low, h/f)'),skipped
          skipped.append((round(r0,2),round(g,2),'breath'));return g,k,skipped
        prev=d;g+=HOP
      if g>=limit:break
      skipped.append((round(r0,2),round(g,2),'breath (detached)'));f=g
    return None,'none',skipped
  def onset(s,st,en,prevStart=None,prevEnd=None):
    """st/en: cue char ASR start/end (frames); prevStart/prevEnd: previous char's ASR start/end (None at sentence start)."""
    lo=max(st-LOOKBACK,prevStart if prevStart is not None else st-LOOKBACK);pe=prevEnd if prevEnd is not None else -1e9
    f=st+HOP
    while f>lo:
      f-=HOP
      if s.db(f)<PAUSE_DB:
        e=f
        while e<en and s.db(e+HOP)<PAUSE_DB:e+=HOP
        b=f
        while b>lo-LOOKBACK and s.db(b-HOP)<PAUSE_DB:b-=HOP
        if e-b+HOP>=PAUSE_MIN and e+HOP>=pe:
          on,kind,sk=s.first_sound(e+HOP,en+3)
          if on is not None:return dict(onset=round(on,2),source='pause',kind=kind,pause=(round(b,2),round(e+HOP,2)),breaths=sk)
        f=b
    return dict(onset=round(st,2),source='asr',kind='continuous',pause=None,breaths=[])
def selftest():
  sr=48000;t=np.arange(sr)/sr;rng=np.random.default_rng(0);seg=lambda a,b:slice(int(a*1600),int(b*1600))
  n=rng.standard_normal(len(t));lp=np.convolve(n,np.ones(24)/24,'same');lp/=np.std(lp);hp=np.diff(n,prepend=0);hp/=np.std(hp)
  # silence, 7 f breath (low-pass -38 dB) straight into 's' (17-20 f), voicing from 20 f -> onset 17, breath skipped
  x=np.zeros_like(t);x[seg(10,17)]=lp[seg(10,17)]*10**(-38/20);x[seg(17,20)]=hp[seg(17,20)]*10**(-28/20);x[seg(20,30)]=0.1*np.sin(2*np.pi*150*t[seg(20,30)])
  r=Rule(x,sr).onset(21.0,30.0);assert abs(r['onset']-17)<=0.5 and r['breaths'],r
  # 3 f 'h'-like low noise straight into voicing -> counts as the consonant, onset 10
  y=np.zeros_like(t);y[seg(10,13)]=lp[seg(10,13)]*10**(-38/20);y[seg(13,20)]=0.1*np.sin(2*np.pi*150*t[seg(13,20)])
  r=Rule(y,sr).onset(13.5,20.0);assert abs(r['onset']-10)<=0.5 and not r['breaths'],r
  # detached breath (10-15 f), 3 f silence, voicing at 18 -> onset 18
  z=np.zeros_like(t);z[seg(10,15)]=lp[seg(10,15)]*10**(-38/20);z[seg(18,25)]=0.1*np.sin(2*np.pi*150*t[seg(18,25)])
  r=Rule(z,sr).onset(19.0,25.0);assert abs(r['onset']-18)<=0.5,r
  return True
if __name__=='__main__':print('selftest',selftest())
