import json
import os
import random
import urllib.request
V = [0,100,320,330,500,900,20000]
R = (16,-16,1,-1)
B = (17,15,-17,-15)
N = (33,31,18,14,-33,-31,-18,-14)
D = R + B
PF = 'pnbrqk'
PST = [
 [0,0,0,0,0,0,0,0,5,10,10,-20,-20,10,10,5,5,-5,-10,0,0,-10,-5,5,
  0,0,0,20,20,0,0,0,5,5,10,25,25,10,5,5,10,10,20,30,30,20,10,10,
  50,50,50,50,50,50,50,50,0,0,0,0,0,0,0,0],
 [-50,-40,-30,-30,-30,-30,-40,-50,-40,-20,0,5,5,0,-20,-40,
  -30,5,10,15,15,10,5,-30,-30,0,15,20,20,15,0,-30,
  -30,5,15,20,20,15,5,-30,-30,0,10,15,15,10,0,-30,
  -40,-20,0,0,0,0,-20,-40,-50,-40,-30,-30,-30,-30,-40,-50],
 [-20,-10,-10,-10,-10,-10,-10,-20,-10,5,0,0,0,0,5,-10,
  -10,10,10,10,10,10,10,-10,-10,0,10,10,10,10,0,-10,
  -10,5,5,10,10,5,5,-10,-10,0,5,10,10,5,0,-10,
  -10,0,0,0,0,0,0,-10,-20,-10,-10,-10,-10,-10,-10,-20],
 [0,0,5,10,10,5,0,0,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,
  -5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,
  5,10,10,10,10,10,10,5,0,0,0,0,0,0,0,0],
 [-20,-10,-10,-5,-5,-10,-10,-20,-10,0,5,0,0,0,0,-10,
  -10,5,5,5,5,5,0,-10,0,0,5,5,5,5,0,-5,-5,0,5,5,5,5,0,-5,
  -10,0,5,5,5,5,0,-10,-10,0,0,0,0,0,0,-10,-20,-10,-10,-5,-5,-10,-10,-20],
 [20,30,10,0,0,10,30,20,20,20,0,0,0,0,20,20,
  -10,-20,-20,-20,-20,-20,-20,-10,-20,-30,-30,-40,-40,-30,-30,-20,
  -30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,
  -30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30],
]
KE = [-50,-30,-30,-30,-30,-30,-30,-50,-30,-30,0,0,0,0,-30,-30,
      -30,-10,20,30,30,20,-10,-30,-30,-10,30,40,40,30,-10,-30,
      -30,-10,30,40,40,30,-10,-30,-30,-10,20,30,30,20,-10,-30,
      -30,-20,-10,0,0,-10,-20,-30,-50,-40,-30,-20,-20,-30,-40,-50]
PST = [None,PST[0],PST[1],PST[2],PST[3],PST[4],PST[5]]
PM = [[0] * 128 for _ in range(13)]
PE = [[0] * 128 for _ in range(13)]
for _q in range(1,7):
    for _s in range(128):
        if _s & 0x88:
            continue
        _i = (_s >> 4) * 8 + (_s & 15)
        _j = (7 - (_s >> 4)) * 8 + (_s & 15)
        PM[_q+6][_s] = V[_q] + PST[_q][_i]
        PM[6-_q][_s] = -V[_q] - PST[_q][_j]
        PE[_q+6][_s] = V[_q] + (KE[_i] if _q == 6 else PST[_q][_i])
        PE[6-_q][_s] = -V[_q] - (KE[_j] if _q == 6 else PST[_q][_j])
def ok(s):
    return 0 <= s < 128 and not (s & 0x88)
def kings(b):
    return {1: b.index(6),-1: b.index(-6)}
def parse(fen):
    f = fen.split()
    b = [0] * 128
    for row,line in enumerate(f[0].split('/')):
        file = 0
        for c in line:
            if c.isdigit():
                file += int(c)
            else:
                b[row * 16 + file] = PF.index(c.lower()) + 1
                if c.islower():
                    b[row * 16 + file] = -b[row * 16 + file]
                file += 1
    return b,(1 if f[1] == 'w' else -1),f[2],\
        ((8 - int(f[3][1])) * 16 + ord(f[3][0]) - 97 if f[3] != '-' else -1),\
        int(f[4]) if len(f)>4 else 0
def attacked(b,s,by):
    for d in (15,17):
        t = s + d * by
        if ok(t) and b[t] == by:
            return True
    for d in N:
        t = s + d
        if ok(t) and b[t] == 2 * by:
            return True
    for d in D:
        t = s + d
        if ok(t) and b[t] == 6 * by:
            return True
    for d in R:
        t = s + d
        while ok(t):
            p = b[t]
            if p:
                if p == 4 * by or p == 5 * by:
                    return True
                break
            t += d
    for d in B:
        t = s + d
        while ok(t):
            p = b[t]
            if p:
                if p == 3 * by or p == 5 * by:
                    return True
                break
            t += d
    return False
def gen(b,side,cast,ep):
    ms = []
    a = ms.append
    for s in range(128):
        if s & 0x88:
            continue
        p = b[s]
        if p * side <= 0:
            continue
        q = abs(p)
        row,file = s >> 4,s & 15
        if q == 1:
            d = -16 * side
            t = s + d
            promo = row == (0 if side == 1 else 7)
            if ok(t) and b[t] == 0:
                if promo:
                    for x in (5,4,3,2): a((s,t,x,0))
                else:
                    a((s,t,0,0))
                    if row == (6 if side == 1 else 1) and b[t + d] == 0:
                        a((s,t + d,0,3))
            for dd in (d - 1,d + 1):
                t = s + dd
                if not ok(t):
                    continue
                if b[t] * side < 0 or t == ep:
                    if promo:
                        for x in (5,4,3,2): a((s,t,x,1 if t == ep else 0))
                    else:
                        a((s,t,0,1 if t == ep else 0))
        elif q == 2:
            for d in N:
                t = s + d
                if ok(t) and b[t] * side <= 0: a((s,t,0,0))
        elif q == 6:
            for d in D:
                t = s + d
                if ok(t) and b[t] * side <= 0: a((s,t,0,0))
            if side == 1 and s == 116:
                if 'K' in cast and not b[117] and not b[118] and not attacked(b,116,-1) and not attacked(b,117,-1) and not attacked(b,118,-1):
                    a((116,118,0,2))
                if 'Q' in cast and not b[115] and not b[114] and not b[113] and not attacked(b,116,-1) and not attacked(b,115,-1) and not attacked(b,114,-1):
                    a((116,114,0,2))
            if side == -1 and s == 4:
                if 'k' in cast and not b[5] and not b[6] and not attacked(b,4,1) and not attacked(b,5,1) and not attacked(b,6,1):
                    a((4,6,0,2))
                if 'q' in cast and not b[3] and not b[2] and not b[1] and not attacked(b,4,1) and not attacked(b,3,1) and not attacked(b,2,1):
                    a((4,2,0,2))
        else:
            dirs = R if q == 4 else B if q == 3 else D
            for d in dirs:
                t = s + d
                while ok(t):
                    if b[t] == 0:
                        a((s,t,0,0))
                    else:
                        if b[t] * side < 0: a((s,t,0,0))
                        break
                    t += d
    return ms
B_,SIDE,CAST,EP,KS,HM = None,1,'',-1,None,0
HASH = MG = EG = MAT = 0
rnd = random.Random(977)
Z = [[rnd.getrandbits(64) for _ in range(128)] for _ in range(13)]
ZS = rnd.getrandbits(64)
ZC = [rnd.getrandbits(64) for _ in range(16)]
ZE = [rnd.getrandbits(64) for _ in range(129)]
def ci(c):
    return sum(1 << 'KQkq'.index(x) for x in c)
def hashall():
    h = mg = eg = mat = 0
    for s in range(128):
        if not (s & 0x88) and B_[s]:
            p = B_[s]
            h ^= Z[p + 6][s]
            mg += PM[p + 6][s]
            eg += PE[p + 6][s]
            if 1 < abs(p) < 6:
                mat += V[abs(p)]
    globals()['MG'] = mg
    globals()['EG'] = eg
    globals()['MAT'] = mat
    if SIDE == -1: h ^= ZS
    return h ^ ZC[ci(CAST)] ^ ZE[EP + 1]
def rights():
    c = ''
    if B_[116] == 6:
        if B_[119] == 4: c += 'K'
        if B_[112] == 4: c += 'Q'
    if B_[4] == -6:
        if B_[7] == -4: c += 'k'
        if B_[0] == -4: c += 'q'
    return c
def setpos(fen):
    global B_,SIDE,CAST,EP,KS,HM,HASH
    B_,SIDE,CAST,EP,HM = parse(fen)
    CAST = rights()
    KS = kings(B_)
    HASH = hashall()
def make(m):
    global SIDE,CAST,EP,HM,HASH,MG,EG,MAT
    f,t,pr,fl = m
    side = SIDE
    moving = B_[f]
    cap = B_[t]
    csq = t
    if fl == 1:
        csq = t + 16 * side
        cap = B_[csq]
    old = (cap,csq,f,moving,CAST,EP,HM,KS[side],HASH,MG,EG,MAT)
    newp = pr * side if pr else moving
    MG += PM[newp+6][t] - PM[moving+6][f]
    EG += PE[newp+6][t] - PE[moving+6][f]
    MAT += (V[abs(newp)] if 1 < abs(newp) < 6 else 0) - (V[abs(moving)] if 1 < abs(moving) < 6 else 0)
    if cap:
        MG -= PM[cap+6][csq]
        EG -= PE[cap+6][csq]
        if 1 < abs(cap) < 6:
            MAT -= V[abs(cap)]
    if fl == 1:
        B_[csq] = 0
    B_[t] = pr * side if pr else moving
    B_[f] = 0
    if fl == 2:
        if t > f:
            B_[t-1] = B_[t+1]; B_[t+1] = 0
        else:
            B_[t+1] = B_[t-2]; B_[t-2] = 0
    if abs(B_[t]) == 6:
        KS[side] = t
    HM = 0 if (abs(moving) == 1 or cap) else HM + 1
    EP = (f + t) // 2 if fl == 3 else -1
    CAST = rights()
    h = HASH ^ Z[moving+6][f] ^ Z[(pr*side if pr else moving)+6][t] ^ ZS
    if cap: h ^= Z[cap+6][csq]
    if fl == 2:
        rt,rf = (t+1,t-1) if t > f else (t-2,t+1)
        rook = B_[rf]
        h ^= Z[rook+6][rf] ^ Z[rook+6][rt]
        MG += PM[rook+6][rt] - PM[rook+6][rf]
        EG += PE[rook+6][rt] - PE[rook+6][rf]
    HASH = h ^ ZC[ci(old[4])] ^ ZC[ci(CAST)] ^ ZE[old[5]+1] ^ ZE[EP+1]
    SIDE = -side
    return old
def unmake(m,old):
    global SIDE,CAST,EP,HM,HASH,MG,EG,MAT
    cap,csq,f,moving,CAST,EP,HM,ksq,HASH,MG,EG,MAT = old
    f,t,pr,fl = m
    B_[f] = moving
    B_[t] = 0
    if fl == 1:
        B_[csq] = cap
    else:
        B_[t] = cap
    if fl == 2:
        if t > f:
            B_[t+1] = B_[t-1]; B_[t-1] = 0
        else:
            B_[t-2] = B_[t+1]; B_[t+1] = 0
    SIDE = -SIDE
    KS[SIDE] = ksq
def evaluate():
    phase = min(MAT,6200)
    return SIDE * ((MG * phase + EG * (6200 - phase)) // 6200)
NODES = 0
STOP = False
LIMIT = 200000
TT = {}
KILL = [[None,None] for _ in range(80)]
HIST = {}
HSTACK = []
def order(ms,ttm,ply):
    k1,k2 = KILL[ply]
    def key(m):
        if m == ttm:
            return 1 << 24
        v = abs(B_[m[1]])
        if v or B_[m[1]] or m[3] == 1:
            return (1 << 20) + v * 16 - V[abs(B_[m[0]])]
        if m == k1: return 1 << 18
        if m == k2: return 1 << 17
        return HIST.get((B_[m[0]],m[1]),0)
    ms.sort(key=key,reverse=True)
    return ms
def qsearch(alpha,beta,ply):
    global NODES,STOP
    NODES += 1
    if NODES > LIMIT:
        STOP = True
        return alpha
    checked = attacked(B_,KS[SIDE],-SIDE)
    if not checked:
        st = evaluate()
        if st >= beta:
            return beta
        if st > alpha:
            alpha = st
    if ply > 16:
        return alpha
    ms = [m for m in gen(B_,SIDE,CAST,EP) if checked or B_[m[1]] or m[2] or m[3] == 1]
    if checked and not ms:
        return -30000+ply
    for m in order(ms,None,ply):
        side = SIDE
        u = make(m)
        if attacked(B_,KS[side],-side):
            unmake(m,u)
            continue
        sc = -qsearch(-beta,-alpha,ply + 1)
        unmake(m,u)
        if sc >= beta:
            return beta
        if sc > alpha:
            alpha = sc
    return alpha
def search(depth,alpha,beta,ply):
    global NODES,STOP,HASH,SIDE,EP
    NODES += 1
    if NODES > LIMIT:
        STOP = True
        return alpha
    if ply and (HASH in HSTACK[:-1] or HM >= 100):
        return 0
    if depth <= 0:
        return qsearch(alpha,beta,ply)
    side = SIDE
    checked = attacked(B_,KS[side],-side)
    if checked:
        depth += 1
    e = TT.get(HASH)
    ttm = None
    if e:
        ttm = e[3]
        if e[0] >= depth and ply:
            if e[2] == 0: return e[1]
            if e[2] == 1 and e[1] >= beta: return e[1]
            if e[2] == 2 and e[1] <= alpha: return e[1]
    if not checked and depth >= 3 and abs(evaluate()) < 2500:
        oldep = EP
        SIDE = -side
        HASH ^= ZS ^ ZE[EP + 1] ^ ZE[0]
        EP = -1
        sc = -search(depth - 3,-beta,-beta + 1,ply + 1)
        SIDE = side
        HASH ^= ZS ^ ZE[EP + 1] ^ ZE[oldep + 1]
        EP = oldep
        if sc >= beta and sc < 30000:
            return beta
    ms = [m for m in gen(B_,SIDE,CAST,EP)]
    if not ms:
        return -30000 + ply if checked else 0
    ms = order(ms,ttm,ply)
    best = -40000
    bm = None
    a0 = alpha
    for i,m in enumerate(ms):
        u = make(m)
        if attacked(B_,KS[side],-side):
            unmake(m,u)
            continue
        HSTACK.append(HASH)
        if i == 0:
            sc = -search(depth - 1,-beta,-alpha,ply + 1)
        else:
            red = 1 if (depth >= 3 and i >= 4 and not B_[m[1]] and not m[2] and not checked) else 0
            sc = -search(depth - 1 - red,-alpha - 1,-alpha,ply + 1)
            if sc > alpha and red:
                sc = -search(depth - 1,-alpha - 1,-alpha,ply + 1)
            if alpha < sc < beta:
                sc = -search(depth - 1,-beta,-alpha,ply + 1)
        HSTACK.pop()
        unmake(m,u)
        if STOP:
            return alpha
        if sc > best:
            best,bm = sc,m
        if sc > alpha:
            alpha = sc
        if alpha >= beta:
            if not B_[m[1]]:
                KILL[ply] = [m,KILL[ply][0]]
                HIST[(B_[m[0]],m[1])] = HIST.get((B_[m[0]],m[1]),0) + depth * depth
            break
    if bm:
        len(TT)>2e5 and TT.clear()
        TT[HASH] = (depth,best,0 if a0 < best < beta else (1 if best >= beta else 2),bm)
    return best
def bestmove(legal):
    global NODES,STOP
    ms = list(legal)
    if not ms:
        return None
    bm = ms[0]
    HSTACK.clear()
    NODES = 0
    STOP = False
    for d in range(1,9):
        ms = sorted(ms,key=lambda m: 0 if m == bm else -1,reverse=True)
        best = -40000
        pick = bm
        a = -40000
        for m in ms:
            side = SIDE
            u = make(m)
            HSTACK.append(HASH)
            sc = -search(d - 1,-a - 1,-a,1)
            if sc > a:
                sc = -search(d - 1,-40000,-a,1)
            HSTACK.pop()
            unmake(m,u)
            if STOP:
                break
            if sc > best:
                best,pick = sc,m
            if sc > a:
                a = sc
        if STOP:
            break
        bm = pick
        if best > 30000:
            break
    return bm
def post(path,body):
    req = urllib.request.Request(os.environ['MAKEFUN_ENV_URL']+path,
        data=json.dumps(body).encode(),headers={'content-type':'application/json'})
    with urllib.request.urlopen(req) as res:
        return json.load(res)
def run():
    while True:
        g = post('/game',{})
        if g['status'] == 'done':
            break
        while g['status'] == 'your_move':
            setpos(g['fen'])
            lm = []
            for m in g['legal_moves']:
                f = (8-int(m[1]))*16 + ord(m[0])-97
                t = (8-int(m[3]))*16 + ord(m[2])-97
                pr = PF.index(m[4])+1 if len(m) == 5 else 0
                fl = 1 if (abs(B_[f]) == 1 and f % 16 != t % 16 and not B_[t]) else 0
                fl = 2 if abs(B_[f]) == 6 and abs(f-t) == 2 else fl
                fl = 3 if abs(B_[f]) == 1 and abs(t-f) == 32 else fl
                lm.append((f,t,pr,fl))
            m = bestmove(lm)
            if m is None:
                post('/resign',{'game': g['game']})
                break
            uci = 'abcdefgh'[m[0]&15] + str(8-(m[0]>>4)) + 'abcdefgh'[m[1]&15] + str(8-(m[1]>>4))
            if m[2]:
                uci += PF[m[2]-1]
            g = post('/move',{'game': g['game'],'move': uci})
if __name__ == '__main__':
    run()
