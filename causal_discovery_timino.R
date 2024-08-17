# -----------------------
# Original TIMINO Routine
# -----------------------

# Independence test routines by Jonas Peters

cross_cov_test <- function(x,eps,alpha,max_lag,plotit=FALSE)
{
  corr1 <- ccf(x,eps,lag.max=max_lag,type = "correlation",plot = FALSE)
  T <- max(abs(corr1$acf))
  sigma <- matrix(0,2*max_lag,2*max_lag)
  # estimate cov of x-cor.
  # Theorem 11.2.3 in brockwell and davis: "bartletts formula"
  # H_0: rho_{12} == 0 => non-zero summands only for j = k - h 
  acr <- acf(x,lag.max=2*max_lag,type = "correlation",plot=FALSE)
  for(i in 1:(2*max_lag))
  {
    for(j in 1:i)
    {
      sigma[i,j]=acr$acf[1+(i-j)]
      sigma[j,i]=acr$acf[1+(i-j)]
    }
  }
  sigma <- sigma/length(x)
  R <- chol(sigma)
  num_simulations<-20000
  z <- matrix(rnorm(2*max_lag*num_simulations),num_simulations,2*max_lag)
  z <- z%*%R
  maxz <- apply(abs(z),1,max)
  maxzorder <- sort(maxz)
  quan <- maxzorder[ceiling(num_simulations-alpha*num_simulations)]
  pval <- sum(maxzorder>T)/num_simulations
  resu <- list(statistic = T, crit.value = quan, p.value = pval)
  return(resu)
}

indtestts_crosscov <- function(z,r1,alpha,max_lag,plotit=FALSE)
{
  z<-as.matrix(z)
  pdim2<-dim(z)
  Tvecquanvec<-c()
  #    Tvecquanvec<-matrix(0,pdim2[2],3)
  Tvec<-matrix(0,pdim2[2],1)
  quanvec<-matrix(0,pdim2[2],1)
  for(i in 1:pdim2[2])
  {
    Tvecquanvec[[i]]<-cross_cov_test(z[,i],r1,alpha/pdim2[2],max_lag,plotit)
    Tvec[i,1]<-Tvecquanvec[[i]]$statistic
    quanvec[i,1]<-Tvecquanvec[[i]]$crit.value
  }
  bb <- which.max(Tvec-quanvec)
  T <- Tvec[bb]
  quan <- quanvec[bb]
  pval <- Tvecquanvec[[bb]]$p.value*pdim2[2]
  resu <- list(statistic = T, crit.value = quan, p.value = pval)
  return(resu)
}


indtestts <- function(f,z,r,alpha,max_lag,plotit=FALSE)
{
  if(plotit == TRUE & 1 == 0)
  {
    par(mfrow = c(2, max_lag + 1))
    len <- dim(as.matrix(r))[1]
    for(i in (-max_lag):(max_lag))
    {
      zz<-as.matrix(z)
      zz<-zz[(max(0,i)+1):(len+min(i,0)),]
      resres<-r[(max(0,i)+1-i):(len+min(i,0)-i)]
      plot(zz,resres)
    }
    readline(prompt = "Plots show the scatter plots between residuals and time series. Press <Enter> to continue...")        
    dev.off()
  }
  
  if(plotit)
  {
    plot.new()
    # readline(prompt = "Plot shows the cross correlation. Press <Enter> to continue...")        
    #par(mfrow = c(2,1))
    ccf(z,r,lag.max=max_lag,type = "correlation",plot = FALSE)
    acf(r)
    readline(prompt = "Plots show cross and auto correlation of the residuals. Press <Enter> to continue...")        
    #dev.off()
  }
  
  result <- f(z,r,alpha,max_lag,plotit)
  if(alpha == 0)
  {
    result$crit.value <- Inf
  }
  return(result)
}

traints_linear <- function(x, Y, pars,plot = FALSE)
{
  if(dim(as.matrix(Y))[1] == 0)
  {
    mod <- ar(x,aic=TRUE,order.max=pars$maxOrder)
    resi <- mod$resid
  }
  else
  {
    mod<-ar(cbind(x,Y),aic=TRUE,order.max=pars$maxOrder)
    resi <- mod$resid[,1] 
  }
  model <- list(order = max(mod$order,1))
  result <- list(residuals = resi, model = model)
}


traints_model <- function(f,x,Y,pars = list(),plot = FALSE)
{
  result <- f(x,Y,pars,plot)
  # sanity check (can be removed)
  if (length(result$residuals) != length(x))
  {
    stop("The length of time series and residuals do not coincide. Check!")
  }
  
  return(result)
}

# This TIMINO Routine part is modified from the following code package. The original license is as follows:

# Copyright (c) 2010-2013 Jonas Peters [peters@stat.math.ethz.ch]
# All rights reserved.  See the file COPYING for license terms. 
#
# This file contains the main implementations for timino causality 
# J. Peters, D. Janzing, B. Schoelkopf: 
# "Causal Inference on Time Series using Restricted Structural Equation Models" (NIPS 2013).
#
# It contains the functions timino_dag and timino_pairwise:
#
# ========
# timino_dag <- function(M, alpha, max_lag, model = traints_linear, indtest = indtestts_crosscov, confounder_check = 0, instant = 0, output = FALSE)
# ==
# INPUT
# M:                nxp matrix with a time series of length n in each column 
# alpha:            significance level of the independence test (when setting to 0 one always obtains a graph estimate, even if the residuals are dependent)
# max_lag:          fit time series up to this order
# model:            assumed time series model (e.g. traints_linear, traints_gam or traints_gp). See fitting_ts.R. 
# indtest:          the independence test that should be performed (e.g. indtestts_hsic or indtestts_crosscov).
# confounder_check: if >0, partial causal discovery method is applied (should be integer).
#                       confounder_check indicates subsets of which size the method tries to omit if it doesn't find any possible sink node
# instant:          are instantaneous effects included (integer number):
#                       instant = 0 means no instantaneous effects allowed
#                       instant = 1 means instantaneous effects allowed
#                       instant = k means we allow shifted time series (arrows from X_t to Y_{t-k+1}).
# check_ind_of_res: if TRUE, the method additionally checks the independence of residuals. 
# ==
# OUTPUT
# Adjacency matrix of the summary time graph; entry (i,j) == 1 indicates that the i-th time series has a causal influence on the j-th time series
# ========
#
#
# ========
# timino_pairwise <- function(x, y, alpha = 0.05, max_lag = 3, model = traints_linear, indtest = indtestts_crosscov, instant = FALSE, check_ind_of_res = FALSE, output = FALSE)
# ==
# INPUT
# x, y: time series of length n
# ==
# OUTPUT
# always NA
# ========


fit_and_test_independence <- function(x, y, z, alpha, max_lag, model, indtest = indtestts_crosscov, instant, check_ind_of_res = FALSE,plotit = FALSE, output = FALSE)
{
  T <- 0
  quan <- 0
  min_lag <- 4
  contr <- 0
  y <- as.matrix(y)
  z <- as.matrix(z)
  pdim <- dim(y)
  pdim2 <- dim(z)
  
  ####
  # fit time series only using x
  ####
  pars1 <- list(maxOrder = max_lag, fixedOrder = max_lag)
  mod_fit <- traints_model(model,x,list(),pars1)
  order1 <- max(mod_fit$model$order,1)
  r1 <- mod_fit$resid[(order1+1):length(x)]
  
  # test independence
  Tquan <- indtestts(indtest,z[(order1+1):length(x),],r1,alpha,max(min_lag,max_lag))
  T <- Tquan$statistic
  quan <- Tquan$crit.value    
  pval <- Tquan$p.value
  #if(T < quan)
  if( (pval > alpha) && (alpha > 0))
  {
    contr<-1
    #quan<-T+0.00000001
    pval <- alpha + 0.0000001
    if(output)
    {
      show('Modelling the first time series without any other leads to independent residuals.')
    }
  }
  else
  {
    ####
    # fit time series using x and y
    ####
    if(instant != FALSE)
    {
      y<-y[-seq(1:instant),]
      x<-x[-seq(length(x) - instant + 1,length(x))]
      # increase max_lag
      max_lag <- max_lag+instant
    }
    
    pars2 <- list(maxOrder = max_lag, fixedOrder = max_lag)
    mod_fit <- traints_model(model,x,y,pars2)
    order2 <- max(mod_fit$model$order,1)
    r2 <- mod_fit$resid[(order2+1):length(x)]
    #show(sprintf("variance of the time series: %.3f. variance of the residuals: %.3f.", var(x), var(r2)))
    # r2b <- ? (needed for check_ind_of_res = TRUE)
    
    
    # checks whether different residuals are independent of each other 
    # r2b<-mod1_fit$resid[(mod1_fit$order+1):length(x),2]},
    if(check_ind_of_res==TRUE)
    {
      stop('This is not implemented yet for traints_gam and traints_gp (residuals r2b are not defined')	
      Tquan <- indtestts(indtest,r2b,r2,alpha,max(min_lag,max_lag+1),plotit)
      T <- Tquan$statistic
      quan <- Tquan$crit.value
      pval <- Tquan$p.value
    }
    else
    {
      Tquan <- indtestts(indtest,z[(order2+1):length(x),],r2,alpha,max(min_lag,max_lag+1),plotit)
      T <- Tquan$statistic
      quan <- Tquan$crit.value
      pval <- Tquan$p.value
    }
  }
  resu <- list(statistic = T, crit.value = quan, p.value = pval, control = contr, order = mod_fit$model$order)
  return(resu)
}




timino_pairwise <- function(x, y, alpha = 0.05, max_lag = 3, model = traints_linear, indtest = indtestts_crosscov, instant = FALSE, check_ind_of_res = FALSE, output = FALSE)
{  
  if(1==1)
  {
    #First, check whether there is any dependence between the two time series. If not, we do not need causal inference.
    show("Checking independence between time series...")
    min_lag <- 4
    # crosscov does not work here because it assumes one of the time series to be white noise.
    pars <- list(maxOrder = max_lag)
    modx <- traints_linear(x,list(),pars)
    mody <- traints_linear(y,list(),pars)
    resx <- modx$residuals[(max(modx$model$order, mody$model$order)+1):length(x)]
    resy <- mody$residuals[(max(modx$model$order, mody$model$order)+1):length(y)]
    
    par(mfrow = c(1,1))
    plot(ccf(resx,resy,lag.max = max_lag))
    readline(prompt = "Plot shows the cross covariance between residuals after fitting univariate models.")
    
    Tquan <- indtestts(indtest,resx,resy,alpha,max(min_lag,max_lag),plotit=TRUE)
    show(sprintf("Test statistic: %.3f, critical value: %.3f, p-value: %.2e", Tquan$statistic,Tquan$crit.value,Tquan$p.value))
    
  }
  else
  {
    Tquan <- c(0,0)
  }
  #if(Tquan$statistic < Tquan$crit.value)
  if(Tquan$p.value < alpha)
  {
    show('After two univariate models were fit, no dependence between the residuals was found. Thus, we stop the causal inference.')
    show('Note that there may still be a causal relationship between x and y, another unobserved time series and a violation of faithfulness.')
  }
  else
  { 
    show("========================")
    show("From 1st to 2nd time series:") 
    Tquanx_to_y<-fit_and_test_independence(y, x, x, alpha, max_lag, model, indtest, instant, check_ind_of_res,plotit=TRUE)
    show(sprintf("Test statistic: %.3f, critical value: %.3f and p-value: %.2e", Tquanx_to_y$statistic,Tquanx_to_y$crit.value,Tquanx_to_y$p.value))
    show(sprintf("The fitted order is: %i",Tquanx_to_y$order))
    
    show("========================")
    show("From 2nd to 1st time series:") 
    Tquany_to_x<-fit_and_test_independence(x, y, y, alpha, max_lag, model, indtest, instant, check_ind_of_res,plotit=TRUE)
    show(sprintf("Test statistic: %.3f and critical value: %.3f and p-value %.2e", Tquany_to_x$statistic,Tquany_to_x$crit.value,Tquany_to_x$p.value))
    show(sprintf("The fitted order is: %i", Tquany_to_x$order))
    
    show("========================")
    xy <- Tquanx_to_y$statistic<Tquanx_to_y$crit.value    
    yalone <- Tquanx_to_y$control == 1
    yx <- Tquany_to_x$statistic<Tquany_to_x$crit.value    
    xalone <- Tquany_to_x$control == 1
    
    if(xalone)
    {
      show('A time series model for x (only using x) renders residuals that are independent of y. but x itself dependents on y. That is a bit strange.')
      show("========================")
      return(0)
    }
    if(yalone)
    {
      show('A time series model for y (only using y) renders residuals that are independent of x. but y itself dependents on x. That is a bit strange.')
      show("========================")
      return(0)
    }
    if(xy & !yalone)
    {
      show('X -> Y')
      if(yx)
      {
        show('But: Y->X is not rejected, either. This is strange. Maybe too few data?')
        show("========================")
        return(0)
      }
      show("========================")   
    }
    if(yx & !xalone)
    {
      show('Y -> X')
      if(xy)
      {
        show('But: X->Y is not rejected, either. This is strange. Maybe too few data?')
        show("========================")
        return(0)
      }
      show("========================")
    }
  }
  return(NA)
}


list_subsets <- function(n,k)
{
  a<-matrix(0,n^k,k)
  for(i in 1:k)
  {
    a[,i] <- rep(1:n,each=n^(k-i),times=n^(i-1))
  }
  for(i in 1:(n^k))
  {
    if(length(unique(a[i,])) < k)
    {
      a <- a[-c(i),]
    }
  }
  return(a)
}





timino_dag <- function(M, alpha, max_lag, model = traints_linear, indtest = indtestts_crosscov, confounder_check = 0, instant = 0, output = FALSE)
{
  stopit <- FALSE
  stopping <- 1
  p <- dim(M)
  C <- matrix(0,p[2],p[2])
  err <- matrix(0,p[2],1)
  S <- 1:p[2]
  par <- matrix(0,p[2]-1,p[2]-1)
  parlen <- rep(0,p[2]-1)
  variable <- rep(0,p[2]-1)
  indtest_at_end <- rep(0,p[2]-1)
  d <- 0
  while(length(S)>1)
  {
    #show(variable)
    d <- d+1
    # check is a vector. the k-th entry < 0 says that making the k-th variable to a sink node leads to independent residuals. 
    check <- rep(0,length(S))
    checkBackup <- rep(0,length(S))
    for(k in 1:length(S))
    {
      i <- S[k]
      S_new <- S
      S_new <- S_new[-c(k)]
      if(output)
      {
        print(paste("fit",i,"with the help of", paste(S_new, collapse=" "),"..."))	
      }
      Fc <- fit_and_test_independence(M[1:p[1],i],M[1:p[1],S_new],M[1:p[1],S_new],alpha,max_lag,model,indtest,instant)
      checkBackup[k] <- Fc$statistic
      #check[k] <- Fc$statistic-Fc$crit.value
      #if(check[k]>0)
      check[k] <- -Fc$p.value
      if(check[k] > -alpha)
      {
        if(output)
        {
          #print(paste("Independence rejected: test statistic - critical value =",check[k]))
          print(paste("Independence rejected: p-value =",-check[k]))
        }
      }
      else
      {
        if(output)
        {
          #print(paste("Independence not rejected: test statistic - critical value =",check[k]))
          print(paste("Independence not rejected: p-value =",-check[k]))
        }
      }
    }
    #if(sum(check<0)==0) #no possible sink node found
    if(sum(check <= -alpha)==0) #no possible sink node found
    {
      if(confounder_check>0 && length(S)>2)
      {
        if(output)
        {
          show("Since no possible sink node was found, the algorithm tries to omit dimensions...")
        }
        for(sizesubset in 1:confounder_check)
        {
          print(paste("tries to omit", sizesubset, "dimension(s) of the time series..."))
          a <- list_subsets(length(S),sizesubset)
          pp <- dim(a)		
          check2 <- matrix(0,pp[1],length(S)-pp[2])
          if(output)
          {
            show("Does omitting variables help?")
          }
          for(k in 1:pp[1])
          {
            #S[a[k,]] werden entfernt
            S_new <- S
            S_new <- S_new[-a[k,]]
            for(kk in 1:length(S_new))
            {
              #Is i possible sink?
              i <- S_new[kk]	                
              S2_new <- S_new
              S2_new <- S2_new[-c(kk)]
              Fc <- fit_and_test_independence(M[1:p[1],i],M[1:p[1],S2_new],M[1:p[1],S2_new],alpha,max_lag,model,indtest,instant)
              #check2[k,kk] <- Fc$statistic-Fc$crit.value
              check2[k,kk] <- -Fc$p.value
              if(output)
              {
                print(paste("omitting: ", paste(S[a[k,]],collapse=" "), "Sink ", i, " leads to ", Fc$statistic-Fc$crit.value, " (<0 independence)."))
              }
            }
          }
          #if(sum(sum(check2<0))>0)
          if(sum(sum(check2< -alpha))>0)
          {
            #found something!
            stopping <- 0
            pp <- dim(check2)
            k1 <- which.min(check2)
            k2 <- (k1-1)%/%pp[1]+1
            k1 <- k1%%pp[1]
            if(k1==0)
            {
              k1 <- pp[1]
            }
            S_new <- S
            S_new <- S_new[-a[k1,]]
            variable[(d):(d+sizesubset-1)] <- S[a[k1,]]
            err[(d):(d+sizesubset-1)] <- rep(1,sizesubset)
            for(iii in 1:sizesubset)
            {
              for(jjj in 1:length(S))
              {
                C[S[a[k1,iii]],S[jjj]] <- -1
                C[S[jjj],S[a[k1,iii]]] <- -1
              }
            }
            
            variable[d+sizesubset] <- S_new[k2]
            S <- S_new[-k2]
            parlen[d+sizesubset] <- length(S)
            par[d+sizesubset,1:length(S)] <- S
            
            d<-d+sizesubset
            break
          }	    
        } # end for
        
        if(stopping==1)
        {
          if(output)
          {
            show("Not even omitting variables helped. Stop the search.")
          }
          err[d:(p[2]-1)] <- rep(1,(p[2]-d))
          for(i in 2:length(S))
          {
            for(j in 1:(i-1))
            {
              C[S[i],S[j]] <- -1
              C[S[j],S[i]] <- -1
            }
          }
          break
        }
        check2 <- rep(0,p[2]-1)
        stopping <- 1
      }
      else # no possible sink node and confounder_check disabled
      {
        if(output)
        {
          show("No possible sink node found. Stop the search.")
        }
        if(confounder_check == 0)
        {
          stopit <- FALSE
        }
        err[d:(p[2]-1)] <- rep(1,(p[2]-d))
        for(i in 2:length(S))
        {
          for(j in 1:(i-1))
          {
            C[S[i],S[j]]<-NA
            C[S[j],S[i]]<-NA
          }
        }
        break
      }
    }
    else #possible sink node found
    {
      if(length(unique(check)) == 1)
      {
        print("since all p-values are the same, we are looking at the statistics...")
        bb <- which.min(checkBackup)
      } else
      {
        bb <- which.min(check)
      }
      variable[d] <- S[bb]
      S <- S[-c(bb)]
      parlen[d] <- length(S)
      par[d,1:length(S)] <- S
      if(output)
      {
        print(paste("Possible sink node found:",variable[d]))
        print(paste("causal order (beginning at sink):",paste(variable,collapse=" ")))
      }	
    }
    rm(check)
  }
  # show(variable)
  if(d<p[2])
  {
    variable[p[2]]<-S[1]
  }
  if(output)
  {
    print(paste("causal order (beginning at sink):",paste(variable,collapse=" ")))
  }
  rm(S)
  
  if(stopit)
  {
    if(output)
    {
      show("STOPPING")
    }
    return(NA)   
  }
  
  
  if(output)
  {
    print(paste("removing unnecessary edges..."))
  }
  #todo: here, we take the first possible parent away (not the best one). in theory it probably shouldn't make a difference. experiments in paper done correctly. but maybe finding all dags is better.
  if(alpha == 0)
  {
    show("Since alpha is zero, we do not remove edges but output a full DAG instead. This corresponds to a causal order of the variables.")
    for(d in 1:(p[2]-1))
    {
      C[par[d,1:parlen[d]],variable[d]] <- 1
    }        
  }else
  {
    for(d in 1:(p[2]-1))
    {
      if(err[d] != 1)
      {
        S<-par[d,1:parlen[d]]
        for(i in 1:length(S))
        {
          S_new<-S
          S_new<-S_new[-c(1)]
          if(length(S)==1)
          {
            # independence test between time series is not
            # Fc <- indtestts(indtestts_hsic,M[1:p[1],variable[d]],M[1:p[1],S],alpha,max_lag,plotit=FALSE)
            # but
            tsx <- M[1:p[1],variable[d]]
            pars <- list(maxOrder = max_lag)
            modx <- traints_model(model,tsx,list(),pars)
            resx <- modx$residuals[(modx$model$order+1):length(tsx)]
            if(output)
            {
              show(par[d,1:parlen[d]])
            }
            # todo: we can either test against par[d,1:parlen[d]] or against S...
            Fc <- indtestts(indtest,ts(M[1:length(resx),par[d,1:parlen[d]]]),resx,alpha,max_lag,plotit=FALSE)
          }
          else
          {
            # todo: we can either test against par[d,1:parlen[d]] or against S...
            Fc <- fit_and_test_independence(M[1:p[1],variable[d]],M[1:p[1],S_new],M[1:p[1],par[d,1:parlen[d]]],alpha,max_lag,model,indtest,instant)
          }
          #if(Fc$statistic<Fc$crit.value)
          if(Fc$p.value > alpha)
          {
            S <- S_new
          }
          else
          {
            if(length(S)>1)
            {
              tmp <- S[1]
              S[1:(length(S)-1)] <- S[2:length(S)]
              S[length(S)] <- tmp
            }
          }
        }
        
        #todo: here, we always perform a final hsic-test
        if(1==0)
        {                 
          if(output)
          {
            print(paste("...and performing final independence test using HSIC..."))
          }
          if(length(S)>0) #if(indtest != indtestts_hsic & length(S)>0)
          {
            if(output)
            {
              print(paste("fitting ", variable[d], " with the help of ", paste(S,collapse=" "), " and testing independence against ", paste(par[d,1:parlen[d]],collapse=" ")))
            }
            Fc <- fit_and_test_independence(M[1:p[1],variable[d]],M[1:p[1],S],M[1:p[1],par[d,1:parlen[d]]],alpha/(p[2]-1),max_lag,model,indtest = indtestts_hsic,instant)
          }
          else
          {
            if(output)
            {
              print(paste("fitting ", variable[d], " with the help of NOTHING and testing independence against ", paste(par[d,1:parlen[d]],collapse=" ")))
            }
            tsx <- M[1:p[1],variable[d]]
            pars <- list(maxOrder = max_lag)
            modx <- traints_model(model,tsx,list(),pars)
            resx <- modx$residuals[(modx$model$order+1):length(tsx)]
            Fc <- indtestts(indtest,M[1:p[1],par[d,1:parlen[d]]],resx,alpha,max_lag,plotit=FALSE)
          }
          if(output)
          {
            show(sprintf("Test statistic: %.3f and critical value: %.3f and p-value %.2e", Fc$statistic,Fc$crit.value,Fc$p.value))        
          }
          #indtest_at_end[d] <- sign(Fc$statistic-Fc$crit.value)
          indtest_at_end[d] <- sign(alpha - Fc$p.value)
          if(confounder_check == 0 && indtest_at_end[d] > 0)
          {
            if(output)
            {
              show("STOPPING")
            }
            return(NA)   
          }
        }
        else
        {
          #-1: ind., +1 dep.
          indtest_at_end[d] <- -1
        }
        parlen[d] <- length(S)
        C[S,variable[d]] <- rep(1,length(S))
      }
      else
      {
        #-1: ind., +1 dep.
        indtest_at_end[d] <- -1
      }
    }
    
    if(max(indtest_at_end)<0)
    {
      for(i in 1:p[2])
      {
        C[i,i] <- 0
      }
      if(output)
      {
        print(paste("all correct..."))
      }
    }
    else
    {
      if(output)
      {
        print(paste("final ind. test failed. No solution."))
      }
      C <- matrix(NA,p[2],p[2])
    }
  }
  if(output)
  {
    show("final summary time graph:")
    show(C)
  }
  return(C)
}

# -------------------------------
# Experimental code for AP report
# -------------------------------
# by Ruijie Tang
# August 2024

time_execution <- function(data, lags) {
  start_time <- Sys.time()
  total_rows <- nrow(data)
  result <- timino_dag(data, alpha = 0.05, max_lag = lags, model = traints_linear, indtest = indtestts_crosscov, output = FALSE)
  end_time <- Sys.time()
  # execution_time <- end_time - start_time
  execution_time <- as.numeric(difftime(end_time, start_time, units = "secs"))
  return(execution_time)
}

record_time <- function(data, n, lags) {
  # n: maximum number of stocks, n is larger than 10
  # execution time is recorded in seconds
  results_df <- data.frame(num_stocks = integer(), execution_time = numeric())
  
  for (i in seq(10, n, 5)) {
    print(i)
    data_subset <- data[, 1:i]
    execution_time <- time_execution(data_subset, lags)
    results_df <- rbind(results_df, data.frame(num_stocks = i, execution_time = execution_time))
  }
  
  write.csv(results_df, file = "execution_times.csv", row.names = FALSE)
}

convert_adj_matrix_to_adj_list <- function(adj_matrix, output_file) {
  # Replace NA values with 0
  adj_matrix[is.na(adj_matrix)] <- 0
  
  # Fill the diagonal with 1
  diag(adj_matrix) <- 1
  
  # Get the number of nodes
  num_nodes <- nrow(adj_matrix)
  
  # Initialize an empty string to hold the adjacency list
  adj_list_string <- ""
  
  # Iterate through each row of the adjacency matrix
  for (i in seq_len(num_nodes)) {
    # Convert row number to zero-based index
    node_name <- i - 1
    
    # Get the neighbors by finding non-zero entries in the row
    neighbors <- which(adj_matrix[i, ] != 0) - 1
    
    # Create the adjacency list line
    adj_list_line <- paste(c(node_name, neighbors), collapse = " ")
    
    # Append the line to the adjacency list string with a newline
    if (i < num_nodes)
    {
      sep <- "\n"
    }
    else
    {
      sep <- ""
    }
    adj_list_string <- paste0(adj_list_string, adj_list_line, sep)
  }
  
  # Write the entire adjacency list string to the file
  writeLines(adj_list_string, con = output_file)
}


run_timino <- function(inputfile, lag, outputfile) {
  data <- read.csv(inputfile)
  graph <- timino_dag(data, alpha = 0.05, max_lag = lag, model = traints_linear, indtest = indtestts_crosscov, output = FALSE)
  convert_adj_matrix_to_adj_list(graph, outputfile)
}
