# Generated by Django 3.2.15 on 2023-08-19 16:32

from django.db import migrations, models

chapter_ids = {
    "Beta": "1tgqSDVbm3heRMi7eFrR9SH1CczwIA0XbL-1T-20rB4g",
    "Chi": "1wNekRkVlmvNPUxxh_Eb2asgmMebHA--19Hu1jeW81so",
    "Chi Beta": "1xtlnh2q3kd6Ix4DpLHuyJL0-ttkTDngkXvLL_3VXBHI",
    "Chi Epsilon": "160u9Bia_6ezGBF6MkXg-xEDFEgXOc_kgrqTrE4QTtXU",
    "Chi Gamma": "1FDHd0ZUpxZTIxryL-84X6YbdPBYR3J07eNnsF-QlrLE",
    "Delta": "1-SUdLwQvq7L7JuLh9HqHcAijgAwZ8g_YiL2NvIxuqLw",
    "Delta Gamma": "1IpkW-tcH9Oa2SAruAMb-Xw0FfK-jyflGzsOVhFxcNCc",
    "Epsilon": "15jFgRCaSdpClq5GvYK3Ye6PkQOZreAi78e_X1St2O28",
    "Epsilon Beta": "1kVzo6rnzDyml2bzwT4xWXA9fYMdTCeErLe7BTSc3-uU",
    "Epsilon Delta": "1YfcwAfkfa-_zvWtjfuwQ2vZz9HnK9r24AtLtUti4YB8",
    "Eta": "15NG4EXzXk9LMRQMn9pBwkdzUH3Yhvj04iFhzZRkYoLs",
    "Eta Delta": "1aDDHsBYPf_cFj0PlTruhtlF3KxiFUOpoZ6eY5MhNQLc",
    "Eta Gamma": "1_-3plrR0bA7Uh-O7FO7EbuILt4nH8lnUBFFn4Nw_VZg",
    "Gamma Beta": "1oQ4jjYWbKeSxWD-gBORpKS1Fe6UNgImPluJGG-ji5xI",
    "Iota Delta": "1ImKIIprxxXMMZdKN486wtShBtU-J964p7gJOt_L0mUU",
    "Iota Epsilon": "1hpjGEJDt_NC1KI-dPSnyXiOS40x04oxISge4zET9pAk",
    "Iota Gamma": "1-ROxH2P7L1exc4XdqU8McKVmRptGcHZugsCfMCB8u_Y",
    "IUPUI Candidate Chapter": "1uB5vqWIZpKGoE8BdrX61zLybgqDkZNb50SuaqJzpvt8",
    "JMU Candidate Chapter": "1tvJXXpwn0cW37K7c9y7EBfEL6VtSiCt9_qGTIVWO1Vk",
    "Kappa": "166Z_-qYp1TLkvisSd4Qzdt0sj1Gu-lRS72K7ugN64ys",
    "Kappa Beta": "1LOTTF0oYQug2MfBMj6srMVbM6MJb_X9ZJpLyFIg-WRI",
    "Kappa Delta": "1AyYXQJMxW4Olfd5VI4UWxMPfzgyXsx3rGjvswlADJzQ",
    "Kappa Epsilon": "1vzeoadvxBgpo6aDE1YuG_dYinP_gah561LkPEfXovUE",
    "Kappa Gamma": "1xIGGAXT9pbsdYzizPuGa5cO9Rw_uDo-aROO_R_Cxg5k",
    "Lambda Delta": "1E1fS39YfTMNbpYwChfUX7KQCWo_JUclGkTO0qnnQEKw",
    "Lambda Epsilon": "1XJm1y3fSC38vbFs8woXFueUaYViRCVTdNIOj_7DgJQQ",
    "Lambda Gamma": "1jE8tHBCgYrEjMYVqEcvZxjKrXRI_D772BtEqit86Zcs",
    "Mu": "1BLbANVMBPBPig5G63lcYh8hfSFX32AtgVmKEGPXaQBo",
    "Mu Delta": "1I4H16f-r41ZMO8wEnMer1XsKUgySfrVf0T5n77UaB-4",
    "Mu Gamma": "1wS_GhQWGPbGHczPdVju8fnipv4AnXv07Xwm1-XlYdm8",
    "Nu Delta": "19pepD_uIf3l8rx_QttKRrCIpfybbKor_qH49_WJgBaY",
    "Nu Epsilon": "1drBm6WM-ex3sEAYNwVz2WxRs_SWb5ESgqaOrldkpHlw",
    "Nu Gamma": "1j1ilqx3ZrgA1nrKVcA_rntKMWulSW1rajbPsgEB1DMc",
    "Omega": "1Rkw8_s9a6GKv9bLaf2TnqEsP4bwOoV9UzB394qCa0hY",
    "Omega Beta": "1vehMseoA_beo7pYJM2Hx8qrUyT8rPl2Mmm4xRse5vsg",
    "Omega Delta": "1jskPycqB-ntrL9kbTzT2dmrmMdfX88gfwnYvT_JxqL0",
    "Omega Epsilon": "1fgRnP_hXcGb9tEO9HRz_mQQHiCKnW8V3SyeIuq5PZww",
    "Omega Gamma": "1R5PddboERtwP8tHkxfXsyT1fzdM923rbar7DU9jT7AA",
    "Omicron": "1pKegayGAq5pHNCnD7Emz9N_VtwDIMFsBBAZwrk1NhbI",
    "Omicron Beta": "1z0BDF70nW5BbajFiyBWJ9sFYzo8-Qa5KV_-znS79gX8",
    "Omicron Delta": "1OeZoHrKy8Ij0d9dIyor6RbPi_RKu7zK8u-536DFzMdk",
    "Omicron Epsilon": "1WJHHaQOETy-Ilpxm2wfyDM-izB71iFHBZ2_gHxuoWIo",
    "Phi": "12t30Ygam5cIMSH6U4SusxWwexie8qgoNoqtMJCpYQn8",
    "Phi Delta": "1tz2aFYT9BYBmT2PTEbSbEBATTDvDOtnV9esV8fOQuKs",
    "Phi Epsilon": "11qSKOFqd28uAlNQs7p9uSkzgre2IooqsRzoE7fPTbyw",
    "Phi Gamma": "1yvMrIUFpxkOXIBGEC6fIctubDkXg681jUjWcCoCzkuc",
    "Pi": "1mLj3uG71h2l4N22_ClsVCc2eR1Flv6lqGfP0tmR0-14",
    "Pi Delta": "1jhxgpumEfao1CPBlhKIcrh2hRw8TBMlvYcYtmN6P0cQ",
    "Pi Epsilon": "1xBxrBmaGNllspDD2jUNTdd3ZiflJX4pZSJLNh76vRao",
    "Psi Beta": "1HJFX7Gg9WSJpULsaOmVlTeCi4prH_YTTD7Z10QxyFmk",
    "Psi Delta": "1-vjC4GENZhkWE98E_G0ZlQiINgkJfZnmNpUEstzoD4Y",
    "Psi Epsilon": "1_5Omye1vQkELcYgWJ_UUnLoDqloplqOh9gl2lBOjbyI",
    "Psi Gamma": "1p_rwAIuac4IN9v-a58XQQxLZG83XKN9fijjikwU5sPU",
    "Rho": "10299HQ5aO1yjLRVg-xat7yTjVQOyYah1pcrW_zJ4G2E",
    "Rho Beta": "1w3COI6KYZ7wMNAiP2BBwUikCcePRBPfT8rFJpC9shNQ",
    "Rho Delta": "12lDPVtPBYyBE2QqseemyuH935cYqcwoRnfBEJZh1RD0",
    "Rho Epsilon": "1IAVN9HFHmO9zab07tt9C5r8vxB664j84hTPLVLdzKV0",
    "Rho Gamma": "1SX3czB7zt50sdlWNvODlyt_8BB8WzFwaSBuS8bnT7y0",
    "Sigma": "1dmAlzSJPEI1JGfjGwjjWxG-37RWhzTxAoKm7Z8MzrTw",
    "Sigma Delta": "1vFDqpvjreAGpBUxiTiRYK5t9q31IEvIvAmTgVZcusQs",
    "Sigma Epsilon": "13mWKvs48w2bAa6qc7gV3Z2kB418c0AkW10h6c2khqfQ",
    "Sigma Gamma": "18zdLIwDoqhJmPfk0PV4RzWVDwRUGxQ9FbX9w1Y0eYdU",
    "SLO Candidate Chapter": "1c8CkBMdyidMdjMjpaNMgI2pk8iDI0vIYIHVhDwOAn_Q",
    "Tau Beta": "1cctDn9Loq9cjF-oKfCZRVq8UHqZnHK8GNnT0RoHQEQQ",
    "Tau Delta": "1izhmmVr0D9SmThKNio7ODHIEG2ZKV9aFnxPyXrnCrYQ",
    "Tau Gamma": "16akh7aCXbntk2sVTAPXszIoKb9q8z3TbXom4fc3d4ic",
    "TEST": "1Waz81onf4aN7XiTCQF9zjDvHnHzh2S2kzQfE44JjXTE",
    "Theta Beta": "150bx4tWdkTrAHbVf0e0qaZpxwdR9IPhhXQ-f816EJxA",
    "Theta Delta": "1Ne52e_qmbTULtgCzy4bbkO2MgBPqkfOnIxN491b1Rec",
    "Theta Epsilon": "1n2MS3y1La9sKMKbOMdSDBoKTWiCPXy8TKfLH5xdBdcY",
    "Theta Gamma": "1w3mdEUAiFw20upW2d9ZrBDBDJ1NiM6fBf01Dh6zL7uY",
    "UNLV Candidate Chapter": "1FSyHVhBm_rN8EDx_HjtGRC9FL30F8BGz8OqxUlbjSAE",
    "Upsilon": "1mQBzTqA0zZKq20NhFGEX21VKmf4Q5efGI_y778E51QM",
    "Upsilon Beta": "17cFpGngGvDFhjt4U9wlgKSRTuZdX1INw_hrewtsZnnk",
    "Upsilon Delta": "123DedLVeExLrZdhqcu-sezhAic9Jtpf5-MyQhzTGU1s",
    "Upsilon Epsilon": "1h5WGf3tBE1oCvcBFMZ8_xOhU4dU5YOEQxmdS8T-kVTI",
    "Upsilon Gamma": "1TWW9tqphWMTChqiAprfjIC1VYElsqiu3kkTz8n8xjwY",
    "Xi": "154t1BQXHJvHwcL6ByvfykM1zJ5Y__tn9kY2-PTSD8kU",
    "Xi Beta": "1aO5hqO4P8oA6oacgPbllijG9xm6AHzx0fk5Cye_2FUc",
    "Xi Delta": "1h9KyYN66j9o6hwsVmfHAFmTItlpZZkvn8lkDWMjjKRc",
    "Xi Epsilon": "1GGBYm5-1Gb5hoXmZTNawUKXIZxSmgyTiE2R4QN5qYhw",
    "Xi Gamma": "1pZafsAn0qg4iv3EboqNxea2BD81CIDbqAR8Dnuwe5f0",
    "Zeta": "1Wj5rP-ytWzU6KENVj1ej61KvAf1_TbDRDrICTH1uj74",
    "Zeta Delta": "1zjZM18BFN7N9VL-wByQVU9B9GTOAcfClTANbbAcgrLE",
    "Zeta Epsilon": "13ULlv3q9mUZbJ_vyq7JIkMQ-1MlrFDs3-WFccT-4LzQ",
    "Zeta Gamma": "1SA7NLjnZgchjsWbn9ypmufWIuJKG_pfPf-O8GLIyQ7w",
}


def set_value(apps, schema_editor):
    chapter = apps.get_model("chapters", "Chapter")
    for chapter in chapter.objects.all():
        if chapter.name not in chapter_ids:
            print(f"No ID for {chapter.name}")
            continue
        id = chapter_ids[chapter.name]
        chapter.nme_file_id = id
        chapter.save(update_fields=["nme_file_id"])


def unset_value(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("chapters", "0012_auto_20220820_1812"),
    ]

    operations = [
        migrations.AddField(
            model_name="chapter",
            name="nme_file_id",
            field=models.CharField(
                default="none",
                help_text="The Google Drive file id for the new member education program",
                max_length=55,
                verbose_name="NME File ID",
            ),
        ),
        migrations.RunPython(set_value, unset_value),
    ]
