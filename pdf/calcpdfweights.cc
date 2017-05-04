#include "mstwpdf.h"
//#include <vector>

// Wrapper around Fortran code for alpha_S.
extern "C" {
  void initalphas_(int *IORD, double *FR2, double *MUR, double *ASMUR,
		   double *MC, double *MB, double *MT);
  double alphas_(double *MUR);
}
inline void InitAlphaS(int IORD, double FR2, double MUR, double ASMUR,
		       double MC, double MB, double MT) {
  initalphas_(&IORD, &FR2, &MUR, &ASMUR,
	      &MC, &MB, &MT);
}
inline double AlphaS(double MUR) {
  return alphas_(&MUR);
}

double Theta(double x1, double x2, double tau){
  double out =0;
  if(x1*x2 > tau) out =1;
  return out;
}

double getDg( double z){

  if(z==0) return 0;
  return (z*z + (1-z)*(1-z))*log((1-z)*(1-z)/z) + 0.5 + 3*z -3.5*z*z;

}


double getError(double a, double b, double ae, double be, string type="sum"){
  if(type == "product"){
    return sqrt( pow(a*be,2) + pow(b*ae,2) ); 
  }
  return sqrt(ae*ae+be*be);
}


int main (void)
{ 

  char filename[100];
  char prefix[] = "Grids/mstw2008nlo"; // prefix for the grid files

  // Consider only the central PDF set to start with.
  sprintf(filename,"%s.%2.2d.dat",prefix,0);
  c_mstwpdf *pdf = new c_mstwpdf(filename); // default: warn=false, fatal=true
  //   bool warn = true;   // option to turn on warnings if extrapolating.
  //   bool fatal = false; // option to return zero instead of terminating if invalid x or q
  //   c_mstwpdf *pdf = new c_mstwpdf(filename,warn,fatal);
  
  // Specify the momentum fraction "x" and scale "q".
  double x = 1e-3, q = 1e2,x2=1e-3;
  double x2g;
  cout << "x = " << x << ", q = " << q << endl;
   
  // Update all PDF flavours.
  pdf->update(x,q);
  // Then the individual flavours are accessed from the cont structure.
  double upv,dnv,usea,dsea,str,sbar,chm,cbar,bot,bbar,glu,phot;
  upv = pdf->cont.upv;
  dnv = pdf->cont.dnv;
  usea = pdf->cont.usea;
  dsea = pdf->cont.dsea;
  str = pdf->cont.str;
  sbar = pdf->cont.sbar;
  chm = pdf->cont.chm;
  cbar = pdf->cont.cbar;
  bot = pdf->cont.bot;
  bbar = pdf->cont.bbar;
  glu = pdf->cont.glu;
  phot = pdf->cont.phot;
  
  // If only a single parton flavour needs to be evaluated,
  // then update(x,q) does not need to be called.
  double upv1,dnv1,usea1,dsea1,str1,sbar1,chm1,cbar1,bot1,bbar1,glu1,phot1;
  upv1 = pdf->parton(8,x,q);
  dnv1 = pdf->parton(7,x,q);
  usea1 = pdf->parton(-2,x,q);
  dsea1 = pdf->parton(-1,x,q);
  str1 = pdf->parton(3,x,q);
  sbar1 = pdf->parton(-3,x,q);
  chm1 = pdf->parton(4,x,q);
  cbar1 = pdf->parton(-4,x,q);
  bot1 = pdf->parton(5,x,q);
  bbar1 = pdf->parton(-5,x,q);
  glu1 = pdf->parton(0,x,q);
  phot1 = pdf->parton(13,x,q);
  // Here the PDG notation is used for the parton flavour
  // (apart from the gluon has f=0, not 21):
  //  f =   -6,  -5,  -4,  -3,  -2,  -1,0,1,2,3,4,5,6
  //    = tbar,bbar,cbar,sbar,ubar,dbar,g,d,u,s,c,b,t.
  // Can also get valence quarks directly:
  //  f =  7, 8, 9,10,11,12.
  //    = dv,uv,sv,cv,bv,tv.
  // Photon: f = 13.
  // Warning: this numbering scheme is different from that used
  // in the MRST2006 NNLO code!
  // (The photon distribution is zero unless considering QED
  // contributions: implemented here for future compatibility.)

  // Demonstrate the equivalence of the above two methods.
  cout << "upv = " << upv << " = " << upv1 << endl;
  cout << "dnv = " << dnv << " = " << dnv1 << endl;
  cout << "usea = " << usea << " = " << usea1 << endl;
  cout << "dsea = " << dsea << " = " << dsea1 << endl;
  cout << "str = " << str << " = " << str1 << endl;
  cout << "sbar = " << sbar << " = " << sbar1 << endl;
  cout << "chm = " << chm << " = " << chm1 << endl;
  cout << "cbar = " << cbar << " = " << cbar1 << endl;
  cout << "bot = " << bot << " = " << bot1 << endl;
  cout << "bbar = " << bbar << " = " << bbar1 << endl;
  cout << "glu = " << glu << " = " << glu1 << endl;
  cout << "phot = " << phot << " = " << phot1 << endl;


  ///////////////////////////////////////////////////////////////////
  // Print out grid ranges, heavy quark masses, and alphaS values. //
  ///////////////////////////////////////////////////////////////////

  cout << "xmin = " << pdf->xmin << ", "
       << "xmax = " << pdf->xmax << ", "
       << "qsqmin = " << pdf->qsqmin << ", "
       << "qsqmax = " << pdf->qsqmax << endl;

  cout << "mCharm = " << pdf->mCharm << ", "
       << "mBottom = " << pdf->mBottom << endl;

  cout << "alphaS(Q0) = " << pdf->alphaSQ0 << ", "
       << "alphaS(MZ) = " << pdf->alphaSMZ << ", "
       << "alphaSorder = " << pdf->alphaSorder << ", "
       << "alphaSnfmax = " << pdf->alphaSnfmax << endl;

  // Call the Fortran initialisation routine with alpha_S(Q_0).
  double FR2 = 1e0, Q0 = 1e0, mTop = 1.e10;
  InitAlphaS(pdf->alphaSorder,FR2,Q0,pdf->alphaSQ0,pdf->mCharm,pdf->mBottom,mTop);

  // Check calculated value of alpha_S(M_Z) matches value stored in grid file.
  double MZ = 91.1876;
  printf("alphaS(MZ) = %7.5f = %7.5f\n",AlphaS(MZ),pdf->alphaSMZ);

  // Alternatively, call the Fortran initialisation routine with alpha_S(M_Z).
  InitAlphaS(pdf->alphaSorder,FR2,MZ,pdf->alphaSMZ,pdf->mCharm,pdf->mBottom,mTop);
  // Check calculated value of alpha_S(Q_0) matches stored value.
  printf("alphaS(Q0) = %7.5f = %7.5f\n",AlphaS(Q0),pdf->alphaSQ0);


  //////////////////////////////////////////////////////////////////////
  // Now demonstrate use of the eigenvector PDF sets.                 //
  //////////////////////////////////////////////////////////////////////

  // Get the central value of the gluon distribution.
  //  sprintf(filename,"%s.%2.2d.dat",prefix,0);
  //  c_mstwpdf *pdf = new c_mstwpdf(filename);
  cout << "central fit: distance = " << pdf->distance << ", tolerance = " << pdf->tolerance << ", glu = " << pdf->parton(0,x,q) << endl;
  // Now get the value of the gluon distribution at a distance t from
  // the global minimum along the first eigenvector direction in the
  // '+' direction.  The distance t is chosen to give a tolerance 
  // T = sqrt(Delta(chi^2_{global})) ensuring all data sets are
  // described within their 90% confidence level (C.L.) limits.
  // Under ideal quadratic behaviour, t = T.
  sprintf(filename,"%s.90cl.%2.2d.dat",prefix,1); // first eigenvector
  c_mstwpdf *pdf90 = new c_mstwpdf(filename);
  cout << "eigenvector +1, 90% C.L.: distance = " << pdf90->distance << ", tolerance = " << pdf90->tolerance << ", glu = " << pdf90->parton(0,x,q) << endl;
  // Now the same thing, but with the tolerance chosen to ensure
  // that all data sets are described only within their
  // one-sigma (68%) C.L. limits.
  sprintf(filename,"%s.68cl.%2.2d.dat",prefix,1); // first eigenvector
  c_mstwpdf *pdf68 = new c_mstwpdf(filename);
  cout << "eigenvector +1, 68% C.L.: distance = " << pdf68->distance << ", tolerance = " << pdf68->tolerance << ", glu = " << pdf68->parton(0,x,q) << endl;

  // Free dynamic memory allocated for "pdf", "pdf90" and "pdf68".
  delete pdf; delete pdf90; delete pdf68;


  ////////////////////////////////////////////////////////////////////////
  // Calculate the uncertainty on the parton distributions using both   //
  // the formula for asymmetric errors [eqs.(51,52) of arXiv:0901.0002] //
  // and the formula for symmetric errors [eq.(50) of same paper].      //
  ////////////////////////////////////////////////////////////////////////

  const int neigen=20; // number of eigenvectors

  // Choose either the 90% C.L. error sets or the 68% C.L. error sets
  char prefix1[100];
  // sprintf(prefix1,"%s.90cl",prefix); // 90% C.L. errors
  sprintf(prefix1,"%s.68cl",prefix); // 68% C.L. errors

  // Create an array of instances of classes "pdfs"
  // to hold the eigenvector sets.
  c_mstwpdf *pdfs[2*neigen+1];
  for (int i=0;i<=2*neigen;i++) {
    if (i==0) sprintf(filename,"%s.%2.2d.dat",prefix,i);
    else sprintf(filename,"%s.%2.2d.dat",prefix1,i);
    pdfs[i] = new c_mstwpdf(filename);
  }

//   // As an alternative to the above create a
//   // vector "pdfs" to hold the eigenvector sets.
//   std::vector<c_mstwpdf*> pdfs;
//   for (int i=0;i<=2*neigen;i++) {
//     if (i==0) sprintf(filename,"%s.%2.2d.dat",prefix,i);
//     else sprintf(filename,"%s.%2.2d.dat",prefix1,i);
//     pdfs.push_back(new c_mstwpdf(filename));
//   }
  
  // First get xf as a function of x at a fixed value of q.
  // Extrapolation will be used for x < 10^-6.
  
  q = 1e2;
  //  double q_i(0);
 

  //



  int nx = 1000;
  double xmin = 1e-7, xmax = 0.99, xf, xfp, xfm, summax, summin, sum;
  double xf2, xfp2, xfm2, summax2, summin2, sum2;
  double  xfq, xfpq, xfmq, summaxq, summinq, sumq;
  double sumq1,sumq2,sumqbar1,sumqbar2;
  double sum1Dq,sum2Dq,SumDqbar1, SumDqbar2;

  double errfx;
  double errfix;
  double errfxbar;
  double errfixbar ;


  double errgluDg1;
  double errgluDg2;
  double errqDg;
  double errqbarDg1;
  double errqbarDg2;


  double fdg,fbardg,fgludg;


  double xfpq1 ;
  double xfmq1 ;
  double xfpq2 ;
  double xfmq2 ;
  double xfpqbar1 ;
  double xfmqbar1 ;
  double xfpqbar2 ;
  double xfmqbar2 ;

  ofstream outfile;
  char buffer[600];
  string flavours[] = {"bbar","cbar","sbar","ubar","dbar","glu",
		       "dn","up","str","chm","bot"};
  double flavContr[5];
  double eflavContr[5];
    string xfilename = "FileWithIntegrals.dat";
    outfile.open(xfilename.c_str());

    for(unsigned int iq=0; iq<=120;iq++)
    {
       q = 80 + 0.25*(iq);
       //  q = 91.50;
	double LO[5], Dg[5], Dq[5];
	double ELO[5], EDg[5], EDq[5];
	double  Total[5];
	double  eTotal[5];
	char AtQ[12];
	sprintf(AtQ,"_q%4.2f",q);
	double S = 8000;
	double tau = q*q/S/S;
	
	string dir = "PDF/";

  for (int flav=-5;flav<0;flav++) {
    cout<<" falv  " <<flavours[flav+5] <<endl;
    string xflav = "x"+flavours[flav+5];

    //>>>>>>>>>>>>>>>> check and write n.o.p
    int npoints(0);
    for (int ix=1;ix<=nx;ix++) {
      x = pow(10.,log10(xmin) + (ix-1.)/(nx-1.)*(log10(xmax)-log10(xmin)));
      if(x >= tau){
	npoints++;
      }
    }
 
    //---------------- LO ---------------
  
    double deltax(0);
    double deltax2(0);
    double integral(0);
    double integralerror(0);
    double integralDg(0);
    double integralDgerror(0);
    xmin = tau;
    xmax = 0.99;
    double Tr = 0.5;
    double x2lo;
    for (int ix=1;ix<=nx;ix++) {
      x = pow(10.,log10(xmin) + (ix-1.)/(nx-1.)*(log10(xmax)-log10(xmin)));
      double xp1 = pow(10.,log10(xmin) + (ix)/(nx-1.)*(log10(xmax)-log10(xmin)));
      double xm1 = pow(10.,log10(xmin) + (ix-2.)/(nx-1.)*(log10(xmax)-log10(xmin)));
      xf = pdfs[0]->parton(flav,x,q); // central set
      if(ix==1) deltax =  (x - xmin)*0.5;
      if(ix==nx) deltax = ( xmax - x) *0.5;
      if(ix!=nx && ix !=1) deltax = ( xp1 - xm1) *0.5;
      x2lo= tau/x;
   
      if(x2lo>0.9999)x2lo=0.99;
      double fx = pdfs[0]->parton(flav,x,q)/x;
      double fix = pdfs[0]->parton(flav,x2lo,q)/x2lo;

      double  fxbar = pdfs[0]->parton(abs(flav),x,q)/x;
      double  fixbar = pdfs[0]->parton(abs(flav),x2lo,q)/x2lo;

      sum = 0.;
      sum2 = 0.;
      errfx = 0.;
      errfix = 0.;
      errfxbar = 0.;
      errfixbar = 0.;
      for (int ieigen=1;ieigen<=neigen;ieigen++) { // loop over eigenvector sets

	errfx +=pow(pdfs[2*ieigen-1]->parton(flav,x,q)/x  - pdfs[2*ieigen]->parton(flav,x,q)/x,2);
	errfix +=pow(pdfs[2*ieigen-1]->parton(flav,x2lo,q)/x2lo  - pdfs[2*ieigen]->parton(flav,x2lo,q)/x2lo,2);
	errfxbar +=pow(pdfs[2*ieigen-1]->parton(abs(flav),x,q)/x  - pdfs[2*ieigen]->parton(abs(flav),x,q)/x,2);
	errfixbar +=pow(pdfs[2*ieigen-1]->parton(abs(flav),x2lo,q)/x2lo  - pdfs[2*ieigen]->parton(abs(flav),x2lo,q)/x2lo,2);
      } 


 
      double LOerr  = 0.25*(ix*fix*errfxbar+ fxbar*fxbar*errfix+fixbar*fixbar*errfx+ fx*fx*errfixbar);

      double factorFromDq = (1 + 4*(2*3.1415*3.1415/3 - 8)*AlphaS(q)/2/3.1415/3);
      integral += factorFromDq*(fix*fxbar + fixbar*fx)*deltax*tau/x/q/q;
      integralerror+=pow(factorFromDq*deltax*tau/x/q/q,2)*LOerr;
 
      for(int ix2=0; ix2 <=nx; ix2++){
	x2g = pow(10.,log10(xmin) + (ix2-1.)/(nx-1.)*(log10(xmax)-log10(xmin)));
	double xp2 = pow(10.,log10(xmin) + (ix2)/(nx-1.)*(log10(xmax)-log10(xmin)));
	double xm2 = pow(10.,log10(xmin) + (ix2-2.)/(nx-1.)*(log10(xmax)-log10(xmin)));

	if(ix2==0) deltax2 = 0.5*(x2g-xmin);
	if(ix2==nx) deltax2 = 0.5*(xmax - x2g);
	if(ix2!=nx && ix2 !=1) deltax2 = ( xp2 - xm2) *0.5;
 
	if(Theta(x,x2,tau)!=0){
	  double pdfactor= pdfs[0]->parton(0,x,q)/x*(pdfs[0]->parton(flav,x2g,q)/x2g  +   pdfs[0]->parton(abs(flav),x2g,q)/x2g) + pdfs[0]->parton(flav,x,q)/x*(pdfs[0]->parton(0,x2g,q)/x2g + pdfs[0]->parton(abs(flav),x2g,q)/x2g);
	  integralDg+=tau*(AlphaS(q)*Tr/2/3.1415)*deltax*deltax2*pdfactor*Theta(x,x2g,tau)*getDg(tau/x/x2g)/x/x2g/q/q;

	  errgluDg1 = 0.;
	  errgluDg2 = 0.;
	  errqDg = 0.;
	  errqbarDg1 = 0.;
	  errqbarDg2 = 0.;
	  for (int ieigen=1;ieigen<=neigen;ieigen++) { // loop over eigenvector sets
	    errgluDg1+=pow(pdfs[2*ieigen-1]->parton(0,x,q)/x  -  pdfs[2*ieigen]->parton(0,x,q)/x,2);
	    errgluDg2+=pow(pdfs[2*ieigen-1]->parton(0,x2g,q)/x2g  -  pdfs[2*ieigen]->parton(0,x2g,q)/x2g,2);
	    errqDg+=pow(pdfs[2*ieigen-1]->parton(abs(flav),x2g,q)/x2g  -  pdfs[2*ieigen]->parton(abs(flav),x2g,q)/x2g,2);
	    errqbarDg1+=pow(pdfs[2*ieigen-1]->parton(flav,x2g,q)/x2  -  pdfs[2*ieigen]->parton(flav,x2g,q)/x2,2);
	    errqbarDg2+=pow(pdfs[2*ieigen-1]->parton(flav,x,q)/x  -  pdfs[2*ieigen]->parton(flav,x,q)/x,2);
	  } 
	  double err1Dg= errqbarDg1  + errqDg;
	  double err2Dg= errgluDg2   + errqDg;
	  double err3Dg = pow((pdfs[0]->parton(flav,x2g,q)/x2  +   pdfs[0]->parton(abs(flav),x2g,q)/x2g),2)*errgluDg1 + pow(pdfs[0]->parton(0,x,q)/x,2)*err1Dg;
	  double err4Dg = pow(pdfs[0]->parton(0,x2g,q)/x2g + pdfs[0]->parton(abs(flav),x2g,q)/x2g,2)*errgluDg1 + pow(pdfs[0]->parton(flav,x,q)/x,2)*err2Dg;
	  double err5Dg =0.25*( err3Dg+err4Dg);

	  integralDgerror+=pow(tau*(AlphaS(q)*Tr/2/3.1415)*deltax*deltax2*Theta(x,x2g,tau)*getDg(tau/x/x2g)/x/x2g/q/q,2)*err5Dg;
	
	}
      }
      //------------ Dg term 
    

    
 
    }

    LO[flav+5]=integral;
    ELO[flav+5]= integralerror;
    Dg[flav+5]=integralDg;
    EDg[flav+5]=integralDgerror;

    cout<<"flav   "<< flav<< "  integral  "<< integral << "  +/-  " << sqrt(integralerror) << endl;
    cout<<"flav   "<< flav<< "  integralDg "<< integralDg << " +/-  "<<sqrt(integralDgerror) <<endl;
 
   int NZ= 100;
   double delta_z = (1-tau)/NZ;
   double FinalIntegral(0);
   double FinalIntegralError(0);
   double IntegralLastTerm(0);

   double lambdamax = 0.99;
   for(int iz = 1; iz < NZ; iz++)
     {

     double z = tau + iz*delta_z;
     double v = sqrt(tau/z);
     int NLambda=100;
     double delta_lambda = (1-v)/NLambda;
     double phiinteg(0);
     double phiintegerror(0);
     double phiintegatzprime1(0);
     double phiintegatzprime1error(0);
     double lambdamin = v;
 
     for(int ilambda = 1; ilambda <=NLambda;ilambda++ ){
     
       
       double  lambda   = pow(10.,log10(lambdamin) + (ilambda-1.)/(NLambda-1.)*(log10(lambdamax)-log10(lambdamin)));
       double  lambdap1 = pow(10.,log10(lambdamin) + (ilambda)/(NLambda-1.)*(log10(lambdamax)-log10(lambdamin)));
       double  lambdam1 = pow(10.,log10(lambdamin) + (ilambda-2.)/(NLambda-1.)*(log10(lambdamax)-log10(lambdamin)));

       if(ilambda==1) delta_lambda =  (lambda - lambdamin)*0.5;
       if(ilambda==NLambda) delta_lambda = ( lambdamax - lambda) *0.5;
       if(ilambda!=NLambda && ilambda !=1) delta_lambda = ( lambdap1 - lambdam1) *0.5;


       double x1 = v/lambda;
       double x2 = v*lambda;
       if(x1>0.9999)x1=0.99; 
     
       double f1 = pdfs[0]->parton(flav,x1,q)/x1;
       double f2 = pdfs[0]->parton(flav,x2,q)/x2;

       double f1bar = pdfs[0]->parton(abs(flav),x1,q)/x1;
       double f2bar = pdfs[0]->parton(abs(flav),x2,q)/x2;
	  
       phiinteg +=(f1*f2bar+f2*f1bar)*delta_lambda/lambda;
       sumq1 = 0.; sumq2= 0.;sumqbar1 = 0.;sumqbar2 = 0.;
       for (int ieigen=1;ieigen<=neigen;ieigen++) { // loop over eigenvector sets

	 xfpq1 = pdfs[2*ieigen-1]->parton(flav,x1,q)/x1; // "+" direction
	 xfmq1 = pdfs[2*ieigen]->parton(flav,x1,q)/x1;   // "-" direction
	 sumq1 += pow(xfpq1-xfmq1,2);

	 xfpq2 = pdfs[2*ieigen-1]->parton(flav,x2,q)/x1; // "+" direction
	 xfmq2 = pdfs[2*ieigen]->parton(flav,x2,q)/x1;   // "-" direction
	 sumq2 += pow(xfpq2-xfmq2,2);

	 xfpqbar1 = pdfs[2*ieigen-1]->parton(abs(flav),x1,q)/x1; // "+" direction
	 xfmqbar1 = pdfs[2*ieigen]->parton(abs(flav),x1,q)/x1;   // "-" direction
	 sumqbar1 += pow(xfpqbar1-xfmqbar1,2);
	 
	 xfpqbar2 = pdfs[2*ieigen-1]->parton(abs(flav),x2,q)/x1; // "+" direction
	 xfmqbar2 = pdfs[2*ieigen]->parton(abs(flav),x2,q)/x1;   // "-" direction
	 sumqbar2 += pow(xfpqbar2-xfmqbar2,2);
       }
       //  cout<<"pdfs[0]->parton(flav,x1,q)  "<< pdfs[0]->parton(flav,x1,q) << "  error   "<<sqrt(sumq1) <<endl;
       double err1 = (pow(f1,2)*sumqbar2 + pow(f2bar,2)*sumq1);
       double err2 = (pow(f2,2)*sumqbar1 + pow(f1bar,2)*sumq2);
       double err3 = (err1 + err2);
       phiintegerror +=err3*pow(delta_lambda/lambda,2);
     }
     for(int ilambda = 1; ilambda <=NLambda;ilambda++ ){//  phi integral at zprime =1
       v = sqrt(tau);
       lambdamin=v;
       double  lambda = pow(10.,log10(lambdamin) + (ilambda-1.)/(NLambda-1.)*(log10(lambdamax)-log10(lambdamin)));
       double  lambdap1 = pow(10.,log10(lambdamin) + (ilambda)/(NLambda-1.)*(log10(lambdamax)-log10(lambdamin)));
       double  lambdam1 = pow(10.,log10(lambdamin) + (ilambda-2.)/(NLambda-1.)*(log10(lambdamax)-log10(lambdamin)));
       
       if(ilambda==1) delta_lambda =  (lambda - lambdamin)*0.5;
       if(ilambda==NLambda) delta_lambda = ( lambdamax - lambda) *0.5;
       if(ilambda!=NLambda && ilambda !=1) delta_lambda = ( lambdap1 - lambdam1) *0.5;

 
       double x1 = v/lambda;
       double x2 = v*lambda;
 
       if(x1>0.9999)x1=0.99;
       double f1 = pdfs[0]->parton(flav,x1,q)/x1;
       double f2 = pdfs[0]->parton(flav,x2,q)/x2;

       double f1bar = pdfs[0]->parton(abs(flav),x1,q)/x1;
       double f2bar = pdfs[0]->parton(abs(flav),x2,q)/x2;
 
       phiintegatzprime1 +=(f1*f2bar+f2*f1bar)*delta_lambda/lambda;
       sum1Dq=0.; sum2Dq=0.; SumDqbar1=0.; SumDqbar2=0.;
       for (int ieigen=1;ieigen<=neigen;ieigen++) { // loop over eigenvector sets
	 sum1Dq +=pow( pdfs[2*ieigen-1]->parton(flav,x1,q)/x1  -  pdfs[2*ieigen]->parton(flav,x1,q)/x1,2);   
	 sum2Dq +=pow( pdfs[2*ieigen-1]->parton(flav,x2,q)/x2  -  pdfs[2*ieigen]->parton(flav,x2,q)/x2,2);   
	 SumDqbar1+=pow( pdfs[2*ieigen-1]->parton(abs(flav),x1,q)/x1  - pdfs[2*ieigen]->parton(abs(flav),x1,q)/x1,2);   
	 SumDqbar2+=pow( pdfs[2*ieigen-1]->parton(abs(flav),x2,q)/x2  -  pdfs[2*ieigen]->parton(abs(flav),x2,q)/x2,2);   
       }

       double err1phiat1 = f1*f1*SumDqbar2 + f2bar*f2bar*sum1Dq;
       double err1phiat2 = f2*f2*sum1Dq    + f1bar*f1bar*SumDqbar2;
       double err1phiat3 = err1phiat1 + err1phiat2;

       phiintegatzprime1error +=err1phiat3*pow(delta_lambda/lambda,2);

     }


     double delta_z1 = tau/NZ;
     for(int iz1=0; iz1<NZ; iz1++){
       double z1 = iz1*delta_z1;
       IntegralLastTerm+=delta_z1*(log(1-z1)/(1-z1));
     }
     double Func =  8*delta_z*(log(1-z)/(1-z)) *((1+z*z)* phiinteg/z - 2*phiintegatzprime1) + 16*phiintegatzprime1*IntegralLastTerm - 4*delta_z*phiinteg*(1+z*z)*log(z)/(1-z)/z;
     double eFunc = 8*pow(2*delta_z*(log(1-z)/(1-z)) *((1+z*z))/z,2)*0.25*phiintegerror +4*0.25*phiintegatzprime1error +  0.25*pow(16*IntegralLastTerm,2)*phiintegatzprime1error + 0.25*pow(4*delta_z*(1+z*z)*log(z)/(1-z)/z,2)*phiintegerror ;

      
     FinalIntegral+=Func;
     FinalIntegralError+=(eFunc);
	
     }
   Dq[flav+5]=4*tau*FinalIntegral*AlphaS(q)/2/3.1415/q/q/3;
   EDq[flav+5]=4*tau*sqrt(FinalIntegralError)*AlphaS(q)/2/3.1415/q/q/3;
   cout<<"LO  " << LO[flav+5] <<  " Dg   "<< Dg[flav+5]  <<"  Dq   " << Dq[flav+5]<<endl;


  }
  Total[4] = LO[4]+Dg[4]+Dq[4];
  Total[3] = LO[3]+Dg[3]+Dq[3];
  Total[2] = LO[2]+Dg[2]+Dq[2];
  Total[1] = LO[1]+Dg[1]+Dq[1];
  Total[0] = LO[0]+Dg[0]+Dq[0];

  eTotal[4] = sqrt(ELO[4]*ELO[4]+EDg[4]*EDg[4]+EDq[4]*EDq[4]);
  eTotal[3] = sqrt(ELO[3]*ELO[3]+EDg[3]*EDg[3]+EDq[3]*EDq[3]);
  eTotal[2] = sqrt(ELO[2]*ELO[2]+EDg[2]*EDg[2]+EDq[2]*EDq[2]);
  eTotal[1] = sqrt(ELO[1]*ELO[1]+EDg[1]*EDg[1]+EDq[1]*EDq[1]);
  eTotal[0] = sqrt(ELO[0]*ELO[0]+EDg[0]*EDg[0]+EDq[0]*EDq[0]);

 
 
   sprintf(buffer,"%12.4E%12.4E%12.4E%12.4E%12.4E%12.4E%12.4E%12.4E%12.4E%12.4E%12.4E",
    	  q,Total[4],eTotal[4],Total[3],eTotal[3], Total[2], eTotal[2],Total[1],eTotal[1],Total[0],eTotal[0]);
   outfile << buffer << endl;
 
  
    }
    outfile.close();


  // Free dynamic memory allocated for "pdfs".
  for (int i=0;i<=2*neigen;i++) {
    delete pdfs[i]; 
  }

  return (0);

}
