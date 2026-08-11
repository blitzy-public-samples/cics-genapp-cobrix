******************************************************************
*  COPYBOOK  : GFNCR001
*  KIND      : RATING-FACTORS
*  COVERAGE  : Damage to Premises Rented to You (Fire Legal Liability) (FL)
*  STATE     : NC
******************************************************************
 01  RT-FNC-RATING.

          03 RT-FNC-TERRITORY-CODE            PIC X(3).
          03 RT-FNC-CLASS-CODE                PIC X(4).
          03 RT-FNC-BASE-RATE                 PIC 9(4)V9(4).
          03 RT-FNC-INCREASED-LIMIT-FACTOR    PIC 9(1)V9(3).
          03 RT-FNC-EXPERIENCE-MOD            PIC 9(1)V9(3).
          03 RT-FNC-SCHEDULE-CREDIT-DEBIT     PIC S9(1)V9(3).
          03 RT-FNC-MINIMUM-PREMIUM           PIC 9(7)V9(2).
          03 RT-FNC-RATED-PREMIUM             PIC 9(9)V9(2).
