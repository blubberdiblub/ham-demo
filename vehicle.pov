#version 3.7;
#include "metals.inc"

#declare AxleTrack = 4;
#declare Wheelbase = 3.6;

global_settings {
	ambient_light rgb <0.4, 0.4, 0.4>
	assumed_gamma 1.0
	charset utf8
}

#declare WheelTexture = texture {
	pigment { rgb <0.3, 0.3, 0.3> }
	finish {
		ambient 0.5
		diffuse 0.5
		specular 0.3
		roughness 0.1
	}
}

#declare AxleTexture = texture {
	T_Chrome_2C
}

#declare CarrierTexture = texture {
	T_Chrome_2B
}

#declare BodyTexture = texture {
	pigment {
		image_pattern {
			jpeg "resources/Pattern2D_01.jpg"
			interpolate 2
			once
		}
		rotate -90 * y
		translate <0, -0.5, -0.2>
		scale <1, 7, 2>
		color_map {
			[0.0 color rgb <1, 1, 0.5>]
			[0.7 color rgb <1, 0.6, 0.1>]
			[1.0 color rgb <1, 0.1, 0.3>]
		}
	}

	finish {
		ambient 0.48
		diffuse 0.48
		reflection { 0.04 }
		specular 0.5
		roughness 0.025
	}
}

#declare WindowTexture = texture {
	pigment { rgb <0.05, 0.05, 0.05> }
	finish {
		ambient 0.3
		diffuse 0.3
		reflection { 0.4 }
		specular 0.5
		roughness 0.1
	}
}

// end of user adjustable properties

#declare Wheel = cylinder {
	-0.6 * x, 0.6 * x, 1
}

#declare Axle = cylinder {
	-AxleTrack/2 * x, AxleTrack/2 * x, 0.15
}

#declare FrontAxleAssembly = union {
	object { Axle texture { AxleTexture } }

	object { Wheel translate -AxleTrack/2 * x texture { WheelTexture } }
	object { Wheel translate  AxleTrack/2 * x texture { WheelTexture } }
}

#declare RearAxleAssembly = union {
	object { Axle texture { AxleTexture } }

	object { Wheel translate -AxleTrack/2 * x texture { WheelTexture } }
	object { Wheel translate  AxleTrack/2 * x texture { WheelTexture } }
}

#declare Chassis = union {
	object { RearAxleAssembly  translate <0, -Wheelbase/2, 0> }
	object { FrontAxleAssembly translate <0,  Wheelbase/2, 0> }
	box {
		<-0.4, -Wheelbase/2 - 0.3, -0.3>,
		< 0.4,  Wheelbase/2 + 0.3,  2>

		texture { CarrierTexture }
	}

	translate z
}

#macro BodyMacro(Length, Width, Height, HoodHeight, CabinFront, FrontAngle, CabinRear, RearAngle, Offset, Overlap)
	difference {
		box {
			<-Width/2 - Offset, -Length/2 - Offset, -Overlap>,
			< Width/2 + Offset,  Length/2 + Offset, Height + Offset>
		}

		intersection {
			plane { -z, -(HoodHeight + Offset) }
			plane {
				-z, -Offset
				rotate -FrontAngle * x
				translate <0, CabinFront, HoodHeight>
			}
		}

		intersection {
			plane { -z, -(HoodHeight + Offset) }
			plane {
				-z, -Offset
				rotate RearAngle * x
				translate <0, CabinRear, HoodHeight>
			}
		}
	}
#end

#macro SideWindowOpening(Height, HoodHeight, CabinFront, FrontAngle, CabinRear, RearAngle, TopOffset, FrontOffset, RearOffset, Offset)
	intersection {
		plane { z, Height + Offset - TopOffset }
		plane { -z, -(HoodHeight + Offset) }

		plane {
			z, Offset - FrontOffset
			rotate -FrontAngle * x
			translate <0, CabinFront, HoodHeight>
		}

		plane {
			z, Offset - RearOffset
			rotate RearAngle * x
			translate <0, CabinRear, HoodHeight>
		}
	}
#end

#macro SideWindow(Width, Height, HoodHeight, CabinFront, FrontAngle, CabinRear, RearAngle, TopOffset, FrontOffset, RearOffset, OutsideOffset, InsideOffset, Overlap)
	intersection {
		union {
			intersection {
				plane { x, Width/2 + OutsideOffset + Overlap }
				plane { -x, -(Width/2 + InsideOffset) + Overlap }
			}

			intersection {
				plane { -x, Width/2 + OutsideOffset + Overlap }
				plane { x, -(Width/2 + InsideOffset) + Overlap }
			}
		}

		SideWindowOpening(Height, HoodHeight, CabinFront, FrontAngle, CabinRear, RearAngle, TopOffset, FrontOffset, RearOffset, OutsideOffset)
	}
#end

#macro Windshield(Width, Height, HoodHeight, CabinFront, FrontAngle, TopOffset, SideOffset, OutsideOffset, InsideOffset, Overlap)
	intersection {
		intersection {
			plane {	z, OutsideOffset + Overlap }
			plane { -z, -InsideOffset + Overlap }

			rotate -FrontAngle * x
			translate <0, CabinFront, HoodHeight>
		}

		plane {  x, Width/2 + OutsideOffset - SideOffset }
		plane { -x, Width/2 + OutsideOffset - SideOffset }

		plane {
			-y, (Height - HoodHeight) / sin(radians(FrontAngle)) - TopOffset
			rotate -FrontAngle * x
			translate <0, CabinFront, HoodHeight>
		}

		plane {
			y, 0
			rotate -FrontAngle/2 * x
			translate <0, CabinFront, HoodHeight>
		}
	}
#end

#declare Body = union {
	difference {
		BodyMacro(5.8, 3, 2.5, 1.5, 1.3, 50, -1, 85, 0, 0)
		BodyMacro(5.8, 3, 2.5, 1.5, 1.3, 50, -1, 85, -0.1, 0.1)
		SideWindowOpening(2.5, 1.5, 1.3, 50, -1, 85, 0.2, 0.2, 0.2, 0)
		Windshield(    3, 2.5, 1.5, 1.3, 50, 0.2, 0.2, 0, -0.1, 0.1)

		cylinder {
			<-1.5 - 0.1, -Wheelbase/2, -0.4>,
			< 1.5 + 0.1, -Wheelbase/2, -0.4>,
			1.03
		}

		cylinder {
			<-1.5 - 0.1, Wheelbase/2, -0.4>,
			< 1.5 + 0.1, Wheelbase/2, -0.4>,
			1.03
		}

		texture { BodyTexture }
	}

	union {
		Windshield(    3, 2.5, 1.5, 1.3, 50, 0.2, 0.2, 0, -0.1, 0.001)
		SideWindow(    3, 2.5, 1.5, 1.3, 50, -1, 85, 0.2, 0.2, 0.2, 0, -0.1, 0.001)

		texture { WindowTexture }
	}
}

#declare Vehicle = union {
	object { Chassis }
	object { Body translate 2 * z }

	scale 30
}

object {
	Vehicle

	rotate clock * 360 * z
}

/*
plane {
	z, 0

	texture {
		pigment {
			checker
			scale 10
		}
	}
}
*/

light_source {
	<1000, -1000, 800>, rgb <1.5, 1.5, 1.5>
	parallel
	point_at <0, 0, 0>
}

#if (image_width < image_height)
	#declare x_aspect = 1;
	#declare y_aspect = image_height / image_width;
#else
	#declare x_aspect = image_width / image_height;
	#declare y_aspect = 1;
#end

#declare Tilt = -degrees(atan(sqrt(1/2))) * x;

camera {
	orthographic
	right 200 * x_aspect * x
	up 200 * y_aspect * z
	direction y
	location <0, -200, 0>

	rotate Tilt
	translate 52 * z
}

#declare Vehicle_Origin = -52 * z * 0 + 100 * x * sqrt(3/2);
#declare Vehicle_Origin = vrotate(Vehicle_Origin, clock * 360 * z);
#declare Camera_Origin = vrotate(100 * y_aspect * z - 100 * x_aspect * x, Tilt);
#declare Camera_X = x;
#declare Camera_Y = vrotate(-z, Tilt);

#declare Delta = Vehicle_Origin - Camera_Origin;
#declare X = vdot(Delta, Camera_X) / (200 * x_aspect / image_width);
#declare Y = vdot(Delta, Camera_Y) / (200 * y_aspect / image_height);

#debug concat(str(X - 160, 0, 12), ", ", str(Y - 100, 0, 12), "\n")
