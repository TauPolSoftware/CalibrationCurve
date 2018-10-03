
// parameters from Madgraph
double hc = 0.38937966E+06; // GeV to nb
double mz = 91.188;
double gz = 2.441404;

double vtau =  -3.68999999999999884e-02;
double atau =  -0.5;
double au   =  0.5;
double ad   =   -0.5;

double pi = 3.14159;
double alpha = 1./132.507;

double qtau =  -1;
double qe   =  -1;
double qd   = -1./3.;
double qu   =  2./3.;

void tree_calc(){


  double energy;
  double sin2theta;

  double xsec_up;
  double pol_up;
  double xsec_down;
  double pol_down;

  double xsec_ele;
  double pol_ele;


  TFile *file = new TFile("tree_calc.root","RECREATE");
  TTree *tree_up= new TTree("tree_up","tree_up");
  
  tree_up->Branch("energy",&energy);
  tree_up->Branch("xsec",&xsec_up);
  tree_up->Branch("pol",&pol_up);
  tree_up->Branch("sin2theta",&sin2theta);
 
  TTree *tree_down= new TTree("tree_down","tree_down");
  
  tree_down->Branch("energy",&energy);
  tree_down->Branch("xsec",&xsec_down);
  tree_down->Branch("pol",&pol_down);
  tree_down->Branch("sin2theta",&sin2theta);
 
  TTree *tree_ele= new TTree("tree_ele","tree_ele");
  
  tree_ele->Branch("energy",&energy);
  tree_ele->Branch("xsec",&xsec_ele);
  tree_ele->Branch("pol",&pol_ele);
  tree_ele->Branch("sin2theta",&sin2theta);


  auto profile_up = new TProfile2D("up_pol_vs_sin2theta_vs_energy","up_pol_vs_sin2theta_vs_energy",100,50,200,100,0.15,0.3,-1,1);
  auto profile_down = new TProfile2D("down_pol_vs_sin2theta_vs_energy","down_pol_vs_sin2theta_vs_energy",100,50,200,100,0.15,0.3,-1,1);
  auto profile_ele = new TProfile2D("ele_pol_vs_sin2theta_vs_energy","ele_pol_vs_sin2theta_vs_energy",100,50,200,100,0.15,0.3,-1,1);

  double q_min=50.;
  double q_max=200.;

  double s2w_min=0.15;
  double s2w_max=0.30;


  double N_q_bins=600;
  double N_s2w_bins=60;


  double q_delta = (q_max - q_min)/N_q_bins;
  double s2w_delta = (s2w_max - s2w_min)/N_s2w_bins;

   for(int j=0; j< N_s2w_bins; j++)
    {
      if(j%5==0) std::cout<<"  step j is at "<< j << "  out of "<< N_s2w_bins <<std::endl;
      double s2wj = s2w_min + j*s2w_delta; //0.23155; //
      for(int i=0; i< N_q_bins; i++)
	{
	  
	  double qi = q_min + i*q_delta;
	  
	  
	  xsec_up = totalXsec(qi, s2wj,"up");
	  xsec_down = totalXsec(qi, s2wj,"down");
	  xsec_ele = totalXsec(qi, s2wj,"ele");
	  pol_up=Pol(qi, s2wj,"up");
	  pol_down=Pol(qi,s2wj,"down");
	  pol_ele=Pol(qi,s2wj,"ele");

	  energy = qi;
	  sin2theta = s2wj;
	  profile_up->Fill(energy,sin2theta,pol_up,1);
	  profile_down->Fill(energy,sin2theta,pol_down,1);
	  profile_ele->Fill(energy,sin2theta,pol_ele,1);
	  tree_up->Fill();
	  tree_down->Fill();
	  tree_ele->Fill();
	}
    }
  file->Write();
  file->Close();
}

Double_t F0(double q, double s2w, string type){
  double s = q*q;
  double sinwcosw4 = 4*s2w*(1. - s2w);
  TComplex chidenom(s-mz*mz,s*gz/mz);
  TComplex chi = (s/sinwcosw4)/chidenom;

  double vf;
  double af;
  double qf;
  if(type=="up")
    {
      af = au;
      vf = au -2*qu*s2w;
      qf = qu;
      //std::cout<<"  ad  "<< af << "  vd  "<< vf <<std::endl;
    }
  if(type=="down")
    {
      af = ad;
      vf = ad -2*qd*s2w;
      qf = qd;
      
    }

  if(type=="ele")
    {
      af = atau;
      vf = vtau;
      qf = qtau;
    }
  return hc*(pi*alpha**2/4/s)*(qtau*qtau*qf*qf + 2*chi.Re()*qtau*qf*vf*vtau + chi.Rho2()*(vtau*vtau+atau*atau)*(vf*vf + af*af));
}

Double_t F1(double q, double s2w, string type){
  double s = q*q;
  double sinwcosw4 = 4*s2w*(1. - s2w);
  TComplex chidenom(s-mz*mz,s*gz/mz);
  TComplex chi = (s/sinwcosw4)/chidenom;

  double vf;
  double af;
  double qf;
  if(type=="up")
    {
      af = au;
      vf = au -2*qu*s2w;
      qf = qu;
    }
  if(type=="down")
    {
      af = ad;
      vf = ad -2*qd*s2w;
      qf = qd;
    }

  if(type=="ele")
    {
      af = atau;
      vf = vtau;
      qf = qtau;
    }

  return hc*(pi*alpha**2/4/s)*( 2*chi.Re()*qtau*qf*af*atau/**sinwcosw4*/ + chi.Rho2()*2*vtau*atau*2*vf*af);
}

Double_t F2(double q, double s2w, string type){
  double s = q*q;
  double sinwcosw4 = 4*s2w*(1. - s2w);
  TComplex chidenom(s-mz*mz,s*gz/mz);
  TComplex chi = (s/sinwcosw4)/chidenom;

  double vf;
  double af;
  double qf;
  if(type=="up")
    {
      af = au;
      vf = au - 2*qu*s2w;
      qf = qu;
    }
  if(type=="down")
    {
      af = ad;
      vf = ad - 2*qd*s2w;
      qf = qd;
    }
  if(type=="ele")
    {
      af = atau;
      vf = vtau;
      qf = qtau;
    }
  return hc*(pi*alpha**2/4/s)*( 2*chi.Re()*qtau*qf*vf*atau + chi.Rho2()*2*vtau*atau*(vf*vf+af*af));
}

Double_t F3(double q, double s2w, string type){
  double s = q*q;
  double sinwcosw4 = 4*s2w*(1. - s2w);
  TComplex chidenom(s-mz*mz,s*gz/mz);
  TComplex chi = (s/sinwcosw4)/chidenom;

  double vf;
  double af;
  double qf;
  if(type=="up")
    {
      af = au;
      vf = au -2*qu*s2w;
      qf = qu;
    }
  if(type=="down")
    {
      af = ad;
      vf = ad -2*qd*s2w;
      qf = qd;
    }
  if(type=="ele")
    {
      af = atau;
      vf = vtau;
      qf = qtau;
    }
  return hc*(pi*alpha**2/4/s)*( 2*chi.Re()*qtau*qf*af*vtau + chi.Rho2()*2*vf*af*(vtau*vtau + atau*atau));
}

Double_t totalXsec(double q, double s2w, string type){    return 16*F0(q,s2w,type)/3; }
Double_t Pol(double q, double s2w, string type){    return -F2(q,s2w,type)/F0(q,s2w,type); }


