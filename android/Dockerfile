FROM archlinux

RUN ldconfig
ENV LANG=en_US.UTF-8

RUN pacman --noconfirm -Sy && \
    pacman --noconfirm -Su base-devel rustup curl python python-pip jre8-openjdk jdk8-openjdk libxtst fontconfig freetype2 \
            lib32-gcc-libs lib32-glibc libxrender cairo gobject-introspection libjpeg-turbo nodejs npm git unzip cmake lld \
            ccache zip && \
    rm -rf /var/cache/pacman/pkg/
RUN rustup toolchain install nightly && rustup target add armv7-linux-androideabi
RUN useradd -m -s /bin/bash -d /build build
RUN echo "build ALL=NOPASSWD: ALL" >> /etc/sudoers
RUN cd /tmp/ && curl https://aur.archlinux.org/cgit/aur.git/snapshot/android-sdk.tar.gz -O &&     tar -xf android-sdk.tar.gz &&     (cd android-sdk && chmod a+rwX . -R && su build -- makepkg -s . && ls -la && pacman --noconfirm -U *.pkg.tar.zst) &&     rm android-sdk.tar.gz android-sdk -rf
RUN yes | /opt/android-sdk/tools/bin/sdkmanager --licenses && /opt/android-sdk/tools/bin/sdkmanager "platforms;android-27" "platforms;android-21" "ndk;23.1.7779620" "tools" "build-tools;28.0.3"
RUN pip install jinja2 Cython
ENV ANDROID_SDK_ROOT=/opt/android-sdk
ENV ANDROID_HOME=/opt/android-sdk
ENV BUILD_TOOLS_VERSION=28.0.3

CMD ["/usr/bin/bash"]

