"""Teaching trace; independently compared with solution and brute-force oracle."""
def trace(nums):
    a, ans, events = sorted(nums), [], []
    def emit(kind, i, l, r, **extra):
        events.append(dict(kind=kind,i=i,l=l,r=r,
            total=a[i]+a[l]+a[r] if i<l<r<len(a) else None,
            result=[x[:] for x in ans],**extra))
    for i in range(len(a)-2):
        if a[i]>0:
            emit('stop',i,i+1,len(a)-1);break
        if i and a[i]==a[i-1]:
            emit('skip-fixed',i,i+1,len(a)-1);continue
        l,r=i+1,len(a)-1
        emit('fix',i,l,r)
        while l<r:
            total=a[i]+a[l]+a[r]
            if total<0:
                emit('low',i,l,r,nextL=l+1);l+=1
            elif total>0:
                emit('high',i,l,r,nextR=r-1);r-=1
            else:
                ans.append([a[i],a[l],a[r]])
                emit('hit',i,l,r)
                left,right=a[l],a[r]
                old=l
                while l<r and a[l]==left:l+=1
                emit('skip-left',i,old,r,nextL=l,value=left)
                old=r
                while l<r and a[r]==right:r-=1
                emit('skip-right',i,l,old,nextR=r,value=right)
        emit('cross',i,l,r)
    return dict(input=nums,sorted=a,result=ans,events=events)
