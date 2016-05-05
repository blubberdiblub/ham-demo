VEHICLE_NUMBERS := $(shell seq -w 0 15)
VEHICLES := $(patsubst %,generated/vehicle%.png,$(VEHICLE_NUMBERS))

FRAME_NUMBERS := $(shell seq -w 0 299)
FRAMES_GIF := $(patsubst %,generated/frame%.gif,$(FRAME_NUMBERS))
FRAMES_PNG := $(patsubst %,generated/frame%.png,$(FRAME_NUMBERS))

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
	gifsicle --loopcount=forever --optimize=2 $(FRAMES_GIF) > $@

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
