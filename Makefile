VEHICLE_NUMBERS := $(shell seq -w 0 15)
VEHICLES := $(patsubst %,generated/vehicle%.png,$(VEHICLE_NUMBERS))

FRAME_NUMBERS := $(shell seq -w 0 316)
FRAMES_GIF := $(patsubst %,generated/frame%.gif,$(FRAME_NUMBERS))
FRAMES_PNG := $(patsubst %,generated/frame%.png,$(FRAME_NUMBERS))

FRAME_NO_PART1 := $(shell seq -f %03.0f 0 65)
FRAME_NO_PART2 := $(shell seq -f %03.0f 66 72)
FRAME_NO_PART3 := $(shell seq -f %03.0f 73 316)
FRAMES_GIF_PART1 := $(patsubst %,generated/frame%.gif,$(FRAME_NO_PART1))
FRAMES_GIF_PART2 := $(patsubst %,generated/frame%.gif,$(FRAME_NO_PART2))
FRAMES_GIF_PART3 := $(patsubst %,generated/frame%.gif,$(FRAME_NO_PART3))

.PHONY: all
all: animation frames atlas background vehicles

.PHONY: animation
animation: generated/animation.gif

.PHONY: frames
frames: $(FRAMES_GIF)

.PHONY: atlas
atlas: generated/atlas.png

.PHONY: background
background: generated/background.png

.PHONY: vehicles
vehicles: $(VEHICLES)

.PHONY: clean
clean:
	rm -f -- generated/*

generated/animation.gif: $(FRAMES_GIF)
	gifsicle --loopcount=forever --optimize=2 \
	--delay=10 $(FRAMES_GIF_PART1) \
	--delay=200 $(FRAMES_GIF_PART2) \
	--delay=10 $(FRAMES_GIF_PART3) \
	> $@

$(FRAMES_GIF): %.gif: %.png
	convert -- $< $@

generated/animation.png: generated/frame000.png
	apngasm $@ $<

generated/frame000.png: ham-demo.py generated/background.png $(VEHICLES) resources/palette.txt
	python3 $<

generated/atlas.png: atlas.py generated/background.png $(VEHICLES)
	python3 $<

generated/background.png: background.ini background.pov
	povray $<

$(VEHICLES): vehicle.ini vehicle.pov resources/Pattern2D_01.jpg
	povray $<
