function normtrace = maxminnorm (x,dim)
    if isvector(x)
    normtrace = (x-min(x))/(max(x)-min(x));
    else
        switch nargin % check how many input arguments are given
            case 1 % "if one is given"
                normtrace = (x-min(x,[],1))./(max(x,[],1)-min(x,[],1)); 
            case 2 % "if two are given"
                normtrace = (x-min(x,[],dim))./(max(x,[],dim)-min(x,[],dim));
        end
    end
end

