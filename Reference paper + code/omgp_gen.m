%
% [x, Y] = omgp_gen(loghyper, n, D, m)
%
% Generate n output data points for m GPs. Each data point is D
% dimensional. The inputs are unidimensional.
%
% loghyper collects the process hyperparameters [log(timescale); 0.5*log(signalPower); 0.5*log(noisePower)]

function [x, Y] = omgp_gen(loghyper, n, D, m)

rs = sum(100*clock);
randn('state',rs); rand('state',rs);

covfunc = {'covSum', {'covSEiso','covNoise'}};

%x = zeros(n*m,1);
Y = zeros(n*m,D);
x = ([1.59179383164442, 1.98724574822052, 2.36805747806268, 2.57961442242197, 2.90841815579740, 2.98582821189663, 3.36554886433977, 3.69193099174221, 3.87333272293030, 4.06586989646427, 4.24775347062622, 4.25822887122662, 4.60562669927342, 5.90147028151262, 6.40973058143213, 6.49872619872079, 6.65290582882933, 7.18852312216145, 7.27574578712792, 7.30643593854807, 7.51216525729664, 8.51594637738672, 9.26331116129353, 9.49114157234113, 9.68550806384046, 9.91614552176422, 10.0995600566108, 10.1490497082835, 10.6411430600643, 10.8273562367179, 11.3435116980159, 11.4002695752538, 11.6662083365186, 11.7000741044571, 11.8616109514322, 11.9105625713640, 12.1198018095748, 13.4310862306541, 13.5007381766079, 13.8568878541673, 13.8998606835519, 13.9607356118026, 14.0162735719598, 14.2863840897013, 15.2960387791029, 15.3848391099917, 15.7396563153646, 15.7516826384958, 15.8961175338559, 15.9057658656030, 16.0940203686051, 16.1402836886706, 17.4375900900850, 17.4760238527489, 17.6193427650044, 17.7599776163929, 18.6337951572861, 18.9465819437975, 19.1599337434421, 19.5751526079905])';

for k = 1:m
    %x((k-1)*n+1:k*n) = rand(n,1)*(n-1)+1;
    Y((k-1)*n+1:k*n,:) = chol(feval(covfunc{:}, loghyper, x((k-1)*n+1:k*n)))'*ones(n,D);  %*randn(n, D);        % Cholesky decomp.
    disp('Y updated');

end

[x, order] = sort(x);
Y = Y(order,:);