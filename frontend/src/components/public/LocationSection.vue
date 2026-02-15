<template>
  <section id="location" class="py-24 px-4 bg-white">
    <div class="max-w-6xl mx-auto">
      <div class="text-center mb-16">
        <span v-reveal="'blur'" class="text-[#86868b] text-sm font-semibold uppercase tracking-[0.2em]">Ubicación</span>
        <h2 v-reveal="'blur'" data-delay="100" class="text-4xl md:text-5xl font-heading font-semibold text-[#1d1d1f] mt-3 tracking-tight">
          Visítanos
        </h2>
        <div v-reveal data-delay="200" class="divider-shimmer w-16 mx-auto mt-5"></div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <!-- Map -->
        <div v-reveal="'left'" class="rounded-2xl overflow-hidden h-80 lg:h-full min-h-[320px] bg-[#f5f5f7] shadow-sm">
          <iframe
            src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d2954.5!2d-8.6095!3d42.2839!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x0%3A0x0!2zNDLCsDE3JzAyLjAiTiA4wrAzNic0Mi4yIlc!5e0!3m2!1ses!2ses!4v1"
            width="100%"
            height="100%"
            style="border: 0"
            allowfullscreen
            loading="lazy"
            referrerpolicy="no-referrer-when-downgrade"
          ></iframe>
        </div>

        <!-- Info -->
        <div class="space-y-5">
          <div v-reveal="'right'" data-delay="100" class="card-premium bg-white rounded-2xl p-6">
            <h3 class="text-lg font-semibold text-[#1d1d1f] mb-4 flex items-center gap-3">
              <div class="w-9 h-9 bg-[#f5f5f7] rounded-xl flex items-center justify-center">
                <svg class="w-4.5 h-4.5 text-[#1d1d1f]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              Horarios
            </h3>
            <div class="space-y-3 text-sm">
              <div class="flex justify-between text-[#86868b]">
                <span>Lunes a Viernes</span>
                <span class="text-[#1d1d1f] font-medium">9:00 - 20:00</span>
              </div>
              <div class="flex justify-between text-[#86868b]">
                <span>Sábados</span>
                <span class="text-[#1d1d1f] font-medium">9:00 - 20:00</span>
              </div>
              <div class="flex justify-between text-[#86868b]">
                <span>Domingos</span>
                <span class="text-red-400 font-medium">Cerrado</span>
              </div>
            </div>
          </div>

          <div v-reveal="'right'" data-delay="200" class="card-premium bg-white rounded-2xl p-6">
            <h3 class="text-lg font-semibold text-[#1d1d1f] mb-4 flex items-center gap-3">
              <div class="w-9 h-9 bg-[#f5f5f7] rounded-xl flex items-center justify-center">
                <svg class="w-4.5 h-4.5 text-[#1d1d1f]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </div>
              Dirección
            </h3>
            <p class="text-[#1d1d1f]">Camiño do Xote 5, bajo</p>
            <p class="text-[#86868b] text-sm mt-1">36693 Redondela, Pontevedra</p>
          </div>

          <div v-reveal="'right'" data-delay="300" class="card-premium bg-white rounded-2xl p-6">
            <h3 class="text-lg font-semibold text-[#1d1d1f] mb-4 flex items-center gap-3">
              <div class="w-9 h-9 bg-[#f5f5f7] rounded-xl flex items-center justify-center">
                <svg class="w-4.5 h-4.5 text-[#1d1d1f]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                </svg>
              </div>
              Contacto
            </h3>
            <p class="text-[#1d1d1f]">+34 600 000 000</p>
            <p class="text-[#86868b] text-sm mt-1">info@cellarstudio.com</p>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Footer -->
  <footer class="bg-[#1d1d1f] py-12 px-4">
    <div class="max-w-6xl mx-auto">
      <div class="flex flex-col md:flex-row items-center justify-between gap-6">
        <div class="text-center md:text-left">
          <h3 class="text-xl font-heading font-semibold text-white tracking-tight">Cellar Studio</h3>
          <p class="text-sm text-gray-500 mt-1">Barbería Premium</p>
        </div>

        <div class="flex items-center gap-3">
          <a
            href="#"
            class="w-10 h-10 bg-white/5 border border-white/10 rounded-full flex items-center justify-center text-gray-500 hover:text-white hover:border-white/30 hover:bg-white/10 transition-all duration-500 ease-out-expo"
            aria-label="Instagram"
          >
            <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 8zm6.406-11.845a1.44 1.44 0 100 2.881 1.44 1.44 0 000-2.881z"/></svg>
          </a>
          <a
            href="#"
            class="w-10 h-10 bg-white/5 border border-white/10 rounded-full flex items-center justify-center text-gray-500 hover:text-green-400 hover:border-green-500/30 hover:bg-green-500/10 transition-all duration-500 ease-out-expo"
            aria-label="WhatsApp"
          >
            <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>
          </a>
        </div>

        <p class="text-sm text-gray-600">&copy; 2026 Cellar Studio. Todos los derechos reservados.</p>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
</script>
