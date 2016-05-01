#version 3.7;
#include "functions.inc"

global_settings {
	assumed_gamma 1.0
	charset utf8
}

camera {
	orthographic
	right image_width * x
	up -image_height * y
	direction z
	location <image_width/2, image_height/2, -200>
}

#default { 
	finish {
		ambient rgb <1, 1, 1>
		diffuse 0
		brilliance 0
	}
}

#declare p_background = pigment {
	dents
	noise_generator 2
	scale 10
}

// dents
// noise_generator 2
// scale 20
// 0.0003721: 0.1130, 0.1909, 0.2919, 0.4074
// <-931.1459917230, -799.7643692644, -428.9891080773>, 0.6742238850547019

// dents
// noise_generator 2
// scale 15
// 0.0002985: 0.1120, 0.1916, 0.2937, 0.4067
// <8990.3548082631, 14269.2260653904, -817.4396003401>, 0.8000000000000000

// dents
// noise_generator 2
// scale 10
// 0.0000818: 0.1058, 0.1934, 0.3011, 0.4017
// <3185.6254086501, 1148.7529250484, 4368.7748457533>, 0.9275106025870326

/*
#declare S = seed(0);
#declare m = 1000*10;

#declare min_d = 0.001;
#for (i, 0, 10000000)
	#declare p = <(rand(S) * 2 - 1) * m, (rand(S) * 2 - 1) * m, (rand(S) * 2 - 1) * m>;
	#declare f = function {
		pigment {
			p_background
			translate p
		}
	}
	#declare c1 = f(-1.5, 0, 0).gray;
	#declare c2 = f(-0.5, 0, 0).gray;
	#declare c3 = f(0.5, 0, 0).gray;
	#declare c4 = f(1.5, 0, 0).gray;
	#undef f
	#if (c1 < c2 & c2 < c3 & c3 < c4)
		#declare d1 = c1 - 0.1;
		#declare d2 = c2 - 0.2;
		#declare d3 = c3 - 0.3;
		#declare d4 = c4 - 0.4;
		#declare d = d1 * d1 + d2 * d2 + d3 * d3 + d4 * d4;
		#if (d < min_d)
			#declare min_d = d;
			#declare shift = p;
			#debug concat(str(min_d, 0, 7), ": ", str(c1, 0, 4), ", ", str(c2, 0, 4), ", ", str(c3, 0, 4), ", ", str(c4, 0, 4), "\n")
		#end
	#end
#end
#debug concat("<", vstr(3, shift, ", ", 0, 10), ">\n")
*/

//#declare p = shift;
//#declare s = 1;
#declare p = <3185.6254086501, 1148.7529250484, 4368.7748457533>;
#declare s = 0.9275106025870326;

#declare c1 = eval_pigment(pigment { p_background translate p scale s}, <-1.5, 0, 0>).gray;
#declare c2 = eval_pigment(pigment { p_background translate p scale s}, <-0.5, 0, 0>).gray;
#declare c3 = eval_pigment(pigment { p_background translate p scale s}, <0.5, 0, 0>).gray;
#declare c4 = eval_pigment(pigment { p_background translate p scale s}, <1.5, 0, 0>).gray;
#declare d = (c1 - 0.1) * (c1 - 0.1) + (c2 - 0.2) * (c2 - 0.2) + (c3 - 0.3) * (c3 - 0.3) + (c4 - 0.4) * (c4 - 0.4);

#declare e = 0.0001;
#declare e2 = e * 2;
#for (i, 0, 1000)
	#declare c1 = eval_pigment(pigment { p_background translate p scale s }, <-1.5 + e, 0, 0>).gray;
	#declare c2 = eval_pigment(pigment { p_background translate p scale s }, <-0.5 + e, 0, 0>).gray;
	#declare c3 = eval_pigment(pigment { p_background translate p scale s }, <0.5 + e, 0, 0>).gray;
	#declare c4 = eval_pigment(pigment { p_background translate p scale s }, <1.5 + e, 0, 0>).gray;
	#declare d_left = (c1 - 0.1) * (c1 - 0.1) + (c2 - 0.2) * (c2 - 0.2) + (c3 - 0.3) * (c3 - 0.3) + (c4 - 0.4) * (c4 - 0.4);

	#declare c1 = eval_pigment(pigment { p_background translate p scale s }, <-1.5 - e, 0, 0>).gray;
	#declare c2 = eval_pigment(pigment { p_background translate p scale s }, <-0.5 - e, 0, 0>).gray;
	#declare c3 = eval_pigment(pigment { p_background translate p scale s }, <0.5 - e, 0, 0>).gray;
	#declare c4 = eval_pigment(pigment { p_background translate p scale s }, <1.5 - e, 0, 0>).gray;
	#declare d_right = (c1 - 0.1) * (c1 - 0.1) + (c2 - 0.2) * (c2 - 0.2) + (c3 - 0.3) * (c3 - 0.3) + (c4 - 0.4) * (c4 - 0.4);

	#declare c1 = eval_pigment(pigment { p_background translate p scale s }, <-1.5, e, 0>).gray;
	#declare c2 = eval_pigment(pigment { p_background translate p scale s }, <-0.5, e, 0>).gray;
	#declare c3 = eval_pigment(pigment { p_background translate p scale s }, <0.5, e, 0>).gray;
	#declare c4 = eval_pigment(pigment { p_background translate p scale s }, <1.5, e, 0>).gray;
	#declare d_up = (c1 - 0.1) * (c1 - 0.1) + (c2 - 0.2) * (c2 - 0.2) + (c3 - 0.3) * (c3 - 0.3) + (c4 - 0.4) * (c4 - 0.4);

	#declare c1 = eval_pigment(pigment { p_background translate p scale s }, <-1.5, -e, 0>).gray;
	#declare c2 = eval_pigment(pigment { p_background translate p scale s }, <-0.5, -e, 0>).gray;
	#declare c3 = eval_pigment(pigment { p_background translate p scale s }, <0.5, -e, 0>).gray;
	#declare c4 = eval_pigment(pigment { p_background translate p scale s }, <1.5, -e, 0>).gray;
	#declare d_down = (c1 - 0.1) * (c1 - 0.1) + (c2 - 0.2) * (c2 - 0.2) + (c3 - 0.3) * (c3 - 0.3) + (c4 - 0.4) * (c4 - 0.4);

	#declare c1 = eval_pigment(pigment { p_background translate p scale s }, <-1.5, 0, e>).gray;
	#declare c2 = eval_pigment(pigment { p_background translate p scale s }, <-0.5, 0, e>).gray;
	#declare c3 = eval_pigment(pigment { p_background translate p scale s }, <0.5, 0, e>).gray;
	#declare c4 = eval_pigment(pigment { p_background translate p scale s }, <1.5, 0, e>).gray;
	#declare d_back = (c1 - 0.1) * (c1 - 0.1) + (c2 - 0.2) * (c2 - 0.2) + (c3 - 0.3) * (c3 - 0.3) + (c4 - 0.4) * (c4 - 0.4);

	#declare c1 = eval_pigment(pigment { p_background translate p scale s }, <-1.5, 0, -e>).gray;
	#declare c2 = eval_pigment(pigment { p_background translate p scale s }, <-0.5, 0, -e>).gray;
	#declare c3 = eval_pigment(pigment { p_background translate p scale s }, <0.5, 0, -e>).gray;
	#declare c4 = eval_pigment(pigment { p_background translate p scale s }, <1.5, 0, -e>).gray;
	#declare d_forward = (c1 - 0.1) * (c1 - 0.1) + (c2 - 0.2) * (c2 - 0.2) + (c3 - 0.3) * (c3 - 0.3) + (c4 - 0.4) * (c4 - 0.4);

	#declare c1 = eval_pigment(pigment { p_background translate p scale s - e }, <-1.5, 0, 0>).gray;
	#declare c2 = eval_pigment(pigment { p_background translate p scale s - e }, <-0.5, 0, 0>).gray;
	#declare c3 = eval_pigment(pigment { p_background translate p scale s - e }, <0.5, 0, 0>).gray;
	#declare c4 = eval_pigment(pigment { p_background translate p scale s - e }, <1.5, 0, 0>).gray;
	#declare d_shrink = (c1 - 0.1) * (c1 - 0.1) + (c2 - 0.2) * (c2 - 0.2) + (c3 - 0.3) * (c3 - 0.3) + (c4 - 0.4) * (c4 - 0.4);

	#declare c1 = eval_pigment(pigment { p_background translate p scale s + e }, <-1.5, 0, 0>).gray;
	#declare c2 = eval_pigment(pigment { p_background translate p scale s + e }, <-0.5, 0, 0>).gray;
	#declare c3 = eval_pigment(pigment { p_background translate p scale s + e }, <0.5, 0, 0>).gray;
	#declare c4 = eval_pigment(pigment { p_background translate p scale s + e }, <1.5, 0, 0>).gray;
	#declare d_grow = (c1 - 0.1) * (c1 - 0.1) + (c2 - 0.2) * (c2 - 0.2) + (c3 - 0.3) * (c3 - 0.3) + (c4 - 0.4) * (c4 - 0.4);

	#declare d1 = <(d - d_left),  (d - d_up),   (d - d_back)    > / e;
	#declare d2 = <(d_right - d), (d_down - d), (d_forward - d )> / e;
	#declare s1 = (d - d_shrink) / e;
	#declare s2 = (d_grow - d) / e;

	#declare dd = (d2 - d1) / e;
	#declare ss = (s2 - s1) / e;
	//#declare ss = 0;
	#declare squared = vdot(dd, dd) + ss * ss;;
	#if (squared = 0)
		#break
	#end
	#declare dstep = dd / squared;
	#declare sstep = ss / squared;

	#declare len = sqrt(squared);
	#declare de = dd / len * e;
	#declare se = ss / len * e;

	#declare c1 = eval_pigment(pigment { p_background translate p scale s - se}, <-1.5, 0, 0> + de).gray;
	#declare c2 = eval_pigment(pigment { p_background translate p scale s - se}, <-0.5, 0, 0> + de).gray;
	#declare c3 = eval_pigment(pigment { p_background translate p scale s - se}, <0.5, 0, 0> + de).gray;
	#declare c4 = eval_pigment(pigment { p_background translate p scale s - se}, <1.5, 0, 0> + de).gray;
	#declare d_behind = (c1 - 0.1) * (c1 - 0.1) + (c2 - 0.2) * (c2 - 0.2) + (c3 - 0.3) * (c3 - 0.3) + (c4 - 0.4) * (c4 - 0.4);

	#declare c1 = eval_pigment(pigment { p_background translate p scale s + se}, <-1.5, 0, 0> - de).gray;
	#declare c2 = eval_pigment(pigment { p_background translate p scale s + se}, <-0.5, 0, 0> - de).gray;
	#declare c3 = eval_pigment(pigment { p_background translate p scale s + se}, <0.5, 0, 0> - de).gray;
	#declare c4 = eval_pigment(pigment { p_background translate p scale s + se}, <1.5, 0, 0> - de).gray;
	#declare d_ahead = (c1 - 0.1) * (c1 - 0.1) + (c2 - 0.2) * (c2 - 0.2) + (c3 - 0.3) * (c3 - 0.3) + (c4 - 0.4) * (c4 - 0.4);

	#declare dv = (d_ahead - d_behind) / e2;
	#declare p = p - dv * dstep;
	#declare s = max(min(s - dv * sstep, 1.25), 0.8);

	#declare c1 = eval_pigment(pigment { p_background translate p scale s}, <-1.5, 0, 0>).gray;
	#declare c2 = eval_pigment(pigment { p_background translate p scale s}, <-0.5, 0, 0>).gray;
	#declare c3 = eval_pigment(pigment { p_background translate p scale s}, <0.5, 0, 0>).gray;
	#declare c4 = eval_pigment(pigment { p_background translate p scale s}, <1.5, 0, 0>).gray;
	#declare d = (c1 - 0.1) * (c1 - 0.1) + (c2 - 0.2) * (c2 - 0.2) + (c3 - 0.3) * (c3 - 0.3) + (c4 - 0.4) * (c4 - 0.4);
#end

#declare c1 = eval_pigment(pigment { p_background translate p scale s}, <-1.5, 0, 0>).gray;
#declare c2 = eval_pigment(pigment { p_background translate p scale s}, <-0.5, 0, 0>).gray;
#declare c3 = eval_pigment(pigment { p_background translate p scale s}, <0.5, 0, 0>).gray;
#declare c4 = eval_pigment(pigment { p_background translate p scale s}, <1.5, 0, 0>).gray;
#declare d = (c1 - 0.1) * (c1 - 0.1) + (c2 - 0.2) * (c2 - 0.2) + (c3 - 0.3) * (c3 - 0.3) + (c4 - 0.4) * (c4 - 0.4);
#debug concat(str(d, 0, 7), ": ", str(c1, 0, 4), ", ", str(c2, 0, 4), ", ", str(c3, 0, 4), ", ", str(c4, 0, 4), "\n")
#debug concat("<", vstr(3, p, ", ", 0, 10), ">, ", str(s, 0, 16), "\n")

#declare p_transformed = pigment {
	p_background
	translate p
	scale s
}

#declare cm_top = color_map {
	[0.0 color rgb < 3/15,  3/15,  3/15>]
	[0.2 color rgb < 9/15,  3/15,  5/15>]
	[0.4 color rgb <11/15,  3/15,  9/15>]
	[0.6 color rgb < 9/15,  9/15, 11/15>]
	[1.0 color rgb <13/15, 13/15, 15/15>]
}

#declare cm_background = color_map {
	[0.0 color rgb <3/15, 6/15, 3/15>]
	[0.1 color rgb <3/15, 3/15, 3/15>]
	[0.2 color rgb <6/15, 3/15, 3/15>]
	[0.3 color rgb <6/15, 7/15, 3/15>]
	[0.4 color rgb <6/15, 7/15, 6/15>]
	[0.5 color rgb <9/15, 9/15, 9/15>]
	[0.6 color rgb <7/15, 6/15, 6/15>]
	[0.7 color rgb <7/15, 6/15, 3/15>]
	[0.8 color rgb <3/15, 6/15, 3/15>]
	[0.9 color rgb <3/15, 3/15, 3/15>]
	[1.0 color rgb <0/15, 0/15, 0/15>]
}

#declare cm_bottom = color_map {
	[0.0 color rgb <3/15, 6/15, 6/15>]
	[0.1 color rgb <3/15, 4/15, 4/15>]
	[0.2 color rgb <3/15, 5/15, 5/15>]
	[0.3 color rgb <5/15, 6/15, 6/15>]
	[0.4 color rgb <7/15, 7/15, 8/15>]
	[0.5 color rgb <9/15, 9/15, 9/15>]
	[1.0 color rgb <6/15, 6/15, 6/15>]
}

/*
difference {
	box { <0, 0, -198>, <320, 200, 198> }
	box { <1, 1, -199>, <319, 199, 199> }

	texture {
		pigment { color rgb <1, 0, 0> }
	}
}
*/

plane {
	-z, 0

	rotate (degrees(atan(sqrt(1/2))) - 90) * x

	texture {
		pigment {
			pigment_pattern {
				gradient y
				scale 200
				translate -100.5 * y
				scale 5/4
			}
			pigment_map {
				[0.0 p_transformed color_map { cm_top }]
				[0.3 p_transformed color_map { cm_background }]
				[0.5 p_transformed color_map { cm_background }]
				[0.9 p_transformed color_map { cm_bottom }]
			}
		}
	}

	//rotate (degrees(atan(sqrt(1/2))) - 90) * x
	translate <102, 100.5, 0>
}
