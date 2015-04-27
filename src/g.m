function [gRow] = g(a, b)
  %helper function to fill in G matrix used to find the entries of L used to
  %find Q in turn
  gRow = [a(1)*b(1), a(1)*b(2)+a(2)*b(1), a(1)*b(3)+a(3)*b(1), a(2)*b(2), a(2)*b(3)+a(3)*b(2), a(3)*b(3)];
end
