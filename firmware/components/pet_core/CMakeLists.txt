# Add this directory to an ESP-IDF project's EXTRA_COMPONENT_DIRS.
# This is a component, not a complete board firmware.
idf_component_register(
  SRCS "../../../src/game.cpp" "../../../src/save.cpp" "../../../src/sprite.cpp" "../../../src/animation.cpp" "../../../src/input.cpp"
       "../../../src/render.cpp" "../../../src/device.cpp"
  INCLUDE_DIRS "../../../include"
)
target_compile_features(${COMPONENT_LIB} PUBLIC cxx_std_17)
