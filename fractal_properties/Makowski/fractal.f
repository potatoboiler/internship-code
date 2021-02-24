c    This code generates the position coordinates x_i, y_i, z_i, i=1,npart,
c    for the npart spheres in a fractal aggregate.   The fractal scaling
c    is given by 
c
c       npart = k0 (Rg/a)^df
c       
c    where k0: structure factor, df: fractal dimension,, a: sphere radius,
c    Rg: radius of gyration:
c
c    Rg^2 = (1/npart) sum r_i^2
c
c    with r_i: distance from ith sphere to center of mass of cluster.
c
c    The code uses a pseudo-random algorithm to mimick cluster-cluster 
c    aggregation, subject to the constraint that the fractal scaling is
c    identically satisfied for the cluster.   
c
c    input parameters:  all should be obvious except nsamp:  this is the 
c    initial number of spheres from which the npart--sized custer will be
c    generated.   nsamp should be >= npart.   I've used nsamp around 
c    1 - 2 * npart.   
c
c    iccmod=0: the code uses a cluster-cluster algorithm.
c    iccmod=1: the original DLA algorithm:  one sphere at a time
c    is added to the cluster.    Not realistic of typical soot dynamics.




      implicit real*4(a-h,o-z)
      parameter(npd=5000)
      real*4 xp(3,npd)
      character fout*30


10    write(*,'('' npart, nsamp, k0, df, iccmod:'',$)') 
      read(*,*) npart, nsamp, rk,df,iccmod
      write(*,'('' output file:'',$)') 
      read(*,'(a)') fout


      if(fout.ne.' ') open(1,file=fout)


      npart=min(npart,npd)
      nsamp=min(nsamp,npd)
      nsamp=max(nsamp,npart)
      iseed=0
      rkf1=(1./rk)**(1./df)/2.



      call ppclus(npart,nsamp,rkf1,df,iccmod,xp,iseed)


      if(fout.ne.' ') then
         do i=1,npart
c            write(1,'(i5,3f10.4)') i,xp(1,i),xp(2,i),xp(3,i)
            write(1,'(f4.0,3f13.6)') 1., xp(1,i),xp(2,i),
     $                        xp(3,i)            
         enddo
         close(1)
      endif
      
      write(*,'('' more (0/1):'',$)')
      read(*,*) more
      if(more.eq.1) goto 10
      
      end



      function ran3(idum)
      save
c      implicit real*4(m)
c         parameter (mbig=4000000.,mseed=1618033.,mz=0.,fac=2.5e-7)
      parameter (mbig=1000000000,mseed=161803398,mz=0,fac=1.e-9)
      dimension ma(55)
      data iff /0/
10    if(idum.lt.0.or.iff.eq.0)then
        iff=1
        mj=mseed-iabs(idum)
        mj=mod(mj,mbig)
        ma(55)=mj
        mk=1
        do 11 i=1,54
          ii=mod(21*i,55)
          ma(ii)=mk
          mk=mj-mk
          if(mk.lt.mz)mk=mk+mbig
          mj=ma(ii)
11      continue
        do 13 k=1,4
          do 12 i=1,55
            ma(i)=ma(i)-ma(1+mod(i+30,55))
            if(ma(i).lt.mz)ma(i)=ma(i)+mbig
12        continue
13      continue
        inext=0
        inextp=31
        idum=1
      endif
      inext=inext+1
      if(inext.eq.56)inext=1
      inextp=inextp+1
      if(inextp.eq.56)inextp=1
      mj=ma(inext)-ma(inextp)
      if(mj.lt.mz)mj=mj+mbig
      ma(inext)=mj
      ran3=mj*fac
      if(ran3.lt.1.d-8.or.ran3.ge.1.) goto 10
      return
      end



      subroutine ppclus(nptot,nptotsamp,rkf1,df,iccmod,xp,iseed0)
      implicit real*4(a-h,o-z)
      parameter(npd=5000)
      integer iadd(npd),npc(npd)
      integer iarray(3)
      real*4 ran3
      real*4 xp(3,*),xpc(3,npd),xpt(3,npd)

c      rkfc=(1.d0/rkfc1)**dfc


      if(iseed0.le.0) then
c         call gettim(ihr,imin,isec,ihsec)
c         iseed=ihr+imin*60+isec*3600+ihsec*360000
         call itime(iarray)
         iseed=3600*iarray(1)+60*iarray(2)+iarray(3)
      else
         iseed=iseed0
      endif
      nptotsamp=min(nptotsamp,npd)
      if(nptotsamp.lt.nptot) nptotsamp=nptot


10    ran=ran3(iseed)


      do i=1,nptotsamp
         do m=1,3
            xpt(m,i)=0.d0
         enddo
         iadd(i)=i
         npc(i)=1
      enddo


      if(iccmod.lt.0) then
         xm=0.
         do i=1,nptot
            xp(1,i)=2.*i
            xm=xm+xp(1,i)
         enddo
         xm=xm/real(nptot)
         do i=1,nptot
            xp(1,i)=xp(1,i)-xm
         enddo
         return
      endif


      nc=nptotsamp
      do while (nc.gt.1)


20       if(iccmod.eq.0) then
            i=int(real(nc)*ran3(1))+1
         else
            i=1
         endif
         j=int(real(nc)*ran3(1))+1
         if(i.eq.j) goto 20



         ic=min(i,j)
         jc=max(i,j)
         iaddic=iadd(ic)
         iaddjc=iadd(jc)
         npic=npc(ic)
         npjc=npc(jc)



c         write(*,'(7i5)') nc,ic,npic,iaddic,jc,npjc,iaddjc 


         do i=1,npjc
            do m=1,3
               xpc(m,i)=xpt(m,i+iaddjc-1)
            enddo
         enddo
         
         do k=jc-1,ic+1,-1
            do nk=npc(k),1,-1
               i=nk+iadd(k)-1
               j=i+npjc
               do m=1,3
                  xpt(m,j)=xpt(m,i)
               enddo
            enddo
            iadd(k)=iadd(k)+npjc
         enddo


c         do i=iaddic,iaddic+npic-1
c            write(*,'(i4,3e12.4)') i,(xp(m,i),m=1,3)
c         enddo
c         do i=1,npjc
c            write(*,'(i4,3e12.4)') i,(xpc(m,i),m=1,3)
c         enddo


         call combine(npic,xpt(1,iaddic),npjc,xpc,rkf1,df)       


         npc(ic)=npic+npjc


         if(npc(ic).eq.nptot) then
            do i=1,nptot
               j=i+iaddic-1
               do m=1,3
                  xp(m,i)=xpt(m,j)
               enddo
            enddo
            return
         endif


         do j=jc,nc-1
            jp=j+1
            iadd(j)=iadd(jp)
            npc(j)=npc(jp)
         enddo
         nc=nc-1    


      enddo
      goto 10
 
      return
      end



      subroutine combine(np1,xp,npc,xp2,rkf1,df)
      implicit real*4(a-h,o-z)
      parameter(npd=5000)
      real*4 ran3
      real*4 xp(3,npd),xc(3),xpc(3,npd),xp2(3,npd),x1(3),x2(3),
     *       rc1(3),rc2(3)
      nits=10000
      pi=4.*atan(1.d0)


      if(np1.eq.1.and.npc.eq.1) then
         ct=1.-2.*ran3(1)
         phi=2.*pi*ran3(1)
         st=sqrt((1.-ct)*(1.+ct))
         xp(1,1)=st*cos(phi)
         xp(2,1)=st*sin(phi)
         xp(3,1)=ct
         do m=1,3
            xp(m,2)=-xp(m,1)
         enddo
         return
      endif


      if(npc.eq.1) then
         call addone(np1,xp,rkf1,df)
         return
      endif


      rgc=dble(npc)**(1./df)*2.*rkf1
      np3=np1+npc
      rg1=dble(np1)**(1./df)*2.*rkf1
      rg3=dble(np3)**(1./df)*2.*rkf1
      c=sqrt(dble(np3)*(np3*rg3*rg3-np1*rg1*rg1-npc*rgc*rgc)
     *  /dble(npc*(np3-npc)))


      do it=1,nits
         ctc=1.d0-2.*ran3(1)
         stc=sqrt((1.d0-ctc)*(1.d0+ctc))
         pc=2.*pi*ran3(1)
         xc(1)=c*stc*cos(pc)
         xc(2)=c*stc*sin(pc)
         xc(3)=c*ctc
         do i=1,npc
            do m=1,3
               xpc(m,i)=xp2(m,i)+xc(m)
            enddo
         enddo


         call finmin(0,np1,xp,npc,xpc,ic1,ic2,r12)


         if(r12.gt.4.d0) goto 40


         r1=0.
         r2=0.
         do m=1,3
            x1(m)=xp(m,ic1)-xc(m)
            x2(m)=xp2(m,ic2)
            r1=r1+x1(m)*x1(m)
            r2=r2+x2(m)*x2(m)
         enddo
         r1=sqrt(r1)
         r2=sqrt(r2)


         if(abs(r1-r2).gt.2.d0) goto 40


         call ctos(x2,rc2)
         beta=acos(rc2(2))
         alpha=rc2(3)
         call rotate(0,alpha,beta,0.,x1)
         gamma=fatan(x1(2),x1(1))


         call rotate(0,0.,0.,gamma,x1)
         call ctos(x1,rc1)
         ctc=(rc1(1)*rc1(1)+rc2(1)*rc2(1)-4.d0)/(2.*rc1(1)*rc2(1))
         if(abs(ctc).gt.1.d0) goto 40
         tc=acos(ctc)
         betac=tc-acos(rc1(2))


         do i=1,npc
            call rotate(0,alpha,beta,gamma,xp2(1,i))
            call rotate(0,0.,betac,0.,xp2(1,i))
            call rotate(1,alpha,beta,gamma,xp2(1,i))
            do m=1,3
               xpc(m,i)=xp2(m,i)+xc(m)
            enddo
         enddo


         call finmin(0,np1,xp,npc,xpc,ic1,ic2,r12c)


         if(r12c.ge.2.d0) goto 50


40    enddo


      write(*,'('' clusters did not combine'')') 


50    do i=1,npc
         do m=1,3
            xp(m,i+np1)=xpc(m,i)
         enddo
      enddo
      
      do m=1,3
         xc(m)=0.d0
      enddo
      do i=1,np3
         do m=1,3
            xc(m)=xc(m)+xp(m,i)
         enddo
      enddo
      do m=1,3
         xc(m)=xc(m)/dble(np3)
      enddo
      do i=1,np3
         do m=1,3
            xp(m,i)=xp(m,i)-xc(m)
         enddo
      enddo


      
      return
      end
               
               


      real*4 function fatan(y,x)
      real*4 x,y
      if(x.eq.0..and.y.eq.0.) then
         fatan=0.
      else
         fatan=atan2(y,x)
      endif
      return
      end


      subroutine ctos(x,r)
      implicit real*4 (a-h,o-z)
      real*4 x(3),r(3)
      r(1)=sqrt(x(1)*x(1)+x(2)*x(2)+x(3)*x(3))
      if(r(1).eq.0.) then
         r(2)=1.d0
         r(3)=0.d0
      else
        r(2)=x(3)/r(1)
        r(3)=fatan(x(2),x(1))
      endif
      return
      end




      subroutine rotate(idir,alpha,beta,gamma,x)
      implicit real*4 (a-h,o-z)
      real*4 x(3),xt(3)


      sa=sin(alpha)
      ca=cos(alpha)
      sb=sin(beta)
      cb=cos(beta)
      sg=sin(gamma)
      cg=cos(gamma)


      if(idir.eq.0) then


         xt(1)=(ca*cb*cg-sa*sg)*x(1)+(cb*cg*sa+ca*sg)*x(2)
     *          -cg*sb*x(3)
         xt(2)=(-cg*sa-ca*cb*sg)*x(1)+(ca*cg-cb*sa*sg)*x(2)
     *          +sb*sg*x(3)
         xt(3)=ca*sb*x(1)+sa*sb*x(2)+cb*x(3)


      else
         xt(1)=(ca*cb*cg-sa*sg)*x(1)-(cb*sg*ca+sa*cg)*x(2)
     *          +ca*sb*x(3)
         xt(2)=(sg*ca+sa*cb*cg)*x(1)+(ca*cg-cb*sa*sg)*x(2)
     *          +sb*sa*x(3)
         xt(3)=-cg*sb*x(1)+sg*sb*x(2)+cb*x(3)
      endif


      do m=1,3
         x(m)=xt(m)
      enddo
      return
      end



      subroutine finmin(isame,np1,xp,np2,xpc,ic1,ic2,r12)
      implicit real*4(a-h,o-z)
      parameter(npd=5000)
      real*4 xp(3,npd),xpc(3,npd)


      rmin=10000.
      do i=1,np1
         do j=1,np2
            if(isame.eq.0.or.i.ne.j) then
               rij=0.
               do m=1,3
                  x12=xp(m,i)-xpc(m,j)
                  rij=rij+x12*x12
               enddo
               if(rij.lt.rmin) then
                  rmin=rij
                  ic1=i
                  ic2=j
               endif
            endif
         enddo
      enddo


      r12=sqrt(rmin)


      return
      end



      subroutine addone(nptot,xp,rkf1,df)
      parameter(npd=3000)
      implicit real*4(a-h,o-z)
      real*4 ran3
      real*4 xp(3,*),rp(npd)
      integer ijp(npd)
      itmax=20000


      rgn2=0.
      rmax=0.
      do i=1,nptot
         ri=0.
         do m=1,3
            ri=ri+xp(m,i)*xp(m,i)
         enddo
         rgn2=rgn2+ri
         rmax=max(rmax,ri)
      enddo
      rgn2=rgn2/dble(nptot)
      rgn=sqrt(rgn2)
      rmax=sqrt(ri)


      np3=nptot+1
      rg3=dble(np3)**(1./df)*2.*rkf1
      rn2=np3*(np3/real(nptot)*rg3*rg3-rgn2)
      rn=sqrt(rn2)
c
c  check if rn is too big
c
      if(rn-rmax.gt.2.) then
         rn=rmax+1.8
         rn2=rn*rn
         rg32=(rn2/real(np3)+rgn2)*(nptot)/real(np3)
         rg3=sqrt(rg32)
      endif
c
c  find particles that intersect with rn
c
   20 i=1
      do 25 j=1,nptot
         rj2=0.
         do k=1,3
            rj2=rj2+xp(k,j)*xp(k,j)
         enddo
         rj=sqrt(rj2)
         rjn=abs(rj-rn)
         if(rjn.le.2.) then
            ijp(i)=j
            rp(i)=rj
            i=i+1
         endif
   25 continue
      nj=i-1
      do 40 i=1,nj
         ran1=ran3(iseed)
         j=nj*ran1+1
         it=ijp(i)
         ijp(i)=ijp(j)
         ijp(j)=it
         rt=rp(i)
         rp(i)=rp(j)
         rp(j)=rt
   40 continue


      do ij=1,nj


         j=ijp(ij)


         rj=rp(ij)
         rj2=rj*rj
         if(rj+rn.lt.2.) goto 50
         ctj=xp(3,j)/rj
         stj=sqrt((1.-ctj)*(1.+ctj))
         phij=atan2(xp(2,j),xp(1,j))
         sphij=sin(phij)
         cphij=cos(phij)
         ctp=(rn2+rj2-4.)/2./rn/rj
         stp=sqrt((1.-ctp)*(1.+ctp))
c
c  randomly find attachment point
c
         it=0
         do while(it.lt.itmax)


            it=it+1
            ran1=ran3(iseed)
            phi=2.*3.141592654*ran1
            zpp=rn*ctp
            xpp=rn*stp*cos(phi)
            ypp=rn*stp*sin(phi)
            z=zpp*ctj-xpp*stj
            x=(zpp*stj+xpp*ctj)*cphij-ypp*sphij
            y=(zpp*stj+xpp*ctj)*sphij+ypp*cphij
            icon=0
            do i=1,nptot
               xi=x-xp(1,i)
               yi=y-xp(2,i)
               zi=z-xp(3,i)
               ri2=xi*xi+yi*yi+zi*zi
               if(ri2.lt.3.999) icon=1
            enddo
            if(icon.eq.0) goto 80
         enddo


50    enddo


      if(ij.gt.nj) then
         rn=rn+0.01
         rn2=rn*rn
         rg32=(rn2/real(np3)+rgn2)*(nptot)/real(np3)
         rg3=sqrt(rg32)
         write(*,'(''+particle '',i3,'' does not fit.'',
     1            '' new rn, rgn:'',2f8.2)') n,rn,rgn
         goto 20
      endif



c
c  shift coordinates to new origin
c
80    xp(1,np3)=x
      xp(2,np3)=y
      xp(3,np3)=z
      x0=0.
      y0=0.
      z0=0.
      do 120 i=1,np3
         x0=x0+xp(1,i)
         y0=y0+xp(2,i)
         z0=z0+xp(3,i)
  120 continue
      x0=x0/real(np3)
      y0=y0/real(np3)
      z0=z0/real(np3)
      do 130 i=1,np3
         xp(1,i)=xp(1,i)-x0
         xp(2,i)=xp(2,i)-y0
         xp(3,i)=xp(3,i)-z0
  130 continue
      return
      end
