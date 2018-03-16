rectangles(a, w, c, cmd) = (c < 1 ? cmd :                                                       \
                            rectangles(a+w, w, c-1,                                             \
                              sprintf("set object %g rectangle from %g, 0 to %g, %g;\n%s",      \
                                c, a, a+w, f(a), cmd)))

set terminal pdf enhanced font "Helvetica,36" size 25.0cm,25.0cm
set output 'riemann-sum.pdf'
set style rectangle fillcolor rgb '#67E6EC' back
set size square
set format "%.1f"
set xrange [0.0:1.0]
set yrange [0.0:1.0]
set style line 1 lt 1 lw 3 lc rgb "red"
f(x) = (1.0-x**2)
eval rectangles(0, 1.0/5, 5, "")
plot [0:1] f(x) notitle with lines ls 1
